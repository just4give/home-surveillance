import cv2
import sys
from flask import Flask, render_template, Response, request, jsonify
import uuid
from camera import VideoCamera
from flask_basicauth import BasicAuth
from flask_socketio import SocketIO, emit
import time
from datetime import datetime
import threading
from threading import Lock
from polly import Polly
import json
from tempimage import TempImage
import boto3
from boto3.dynamodb.conditions import Key, Attr
import requests
from flask_ngrok import run_with_ngrok
import uuid
from flask_cors import CORS,cross_origin
import base64
# Set this variable to "threading", "eventlet" or "gevent" to test the
# different async modes, or leave it set to None for the application to choose
# the best option based on installed packages.
async_mode = None

conf = json.load(open("conf.json"))


video_camera = VideoCamera(flip=False) # creates a camera object, flip vertically
object_classifier = cv2.CascadeClassifier("models/haarcascade_frontalface_alt.xml") # an opencv classifier

# App Globals (do not edit)
app = Flask(__name__)
app.config['BASIC_AUTH_USERNAME'] = conf["flask_username"]
app.config['BASIC_AUTH_PASSWORD'] = conf["flask_password"]
app.config['BASIC_AUTH_FORCE'] = False

app.config['SECRET_KEY'] = 'secret!'

CORS(app, resources={ r'/*': {'origins': '*'}}, supports_credentials=True)
socketio = SocketIO(app, async_mode=async_mode)
#run_with_ngrok(socketio) 
thread = None
thread_lock = Lock()
polly = Polly('Joanna')

s3client = boto3.resource('s3')
rekoclient=boto3.client('rekognition')
dynamodb = boto3.resource('dynamodb')
dbPiFaces = dynamodb.Table('PiFaces')
dbPiNgRok = dynamodb.Table('PiNgRok')
dbPiMessages = dynamodb.Table('PiMessages')
dbPiNotification= dynamodb.Table('PiNotification')
expiresIn=5*24*3600 #expires recorded voice after 5 days

basic_auth = BasicAuth(app)
last_epoch = 0
last_upload = 0
motionCounter = 0

def sortKey(e):
  return e['Similarity']

def scanMessages():
    response = dbPiMessages.scan()
    return response['Items']

def deleteMessage(id,createdOn):
    print("deleting message ",id)
    dbPiMessages.delete_item(
        Key={
            'id': id,
            'createdOn':createdOn
        }
    )
def deleteNotification(id,createdOn):
    print("deleting message ",id)
    dbPiNotification.delete_item(
        Key={
            'id': id,
            'createdOn':createdOn
        }
    )
def updateNotification(id,createdOn,faceId,faceName):
    dbPiNotification.update_item(
        Key ={
            'id': id,
            'createdOn':createdOn
        },
        UpdateExpression='SET faceId = :faceId, faceName=:faceName',
        ExpressionAttributeValues={
            ':faceName': faceName,
            ':faceId': faceId
        }
    )


def scanFaces():
    response = dbPiFaces.scan()
    data= response['Items']
    #signedUrl = s3client.meta.client.generate_presigned_url('get_object', Params = {'Bucket': conf["s3bucket_name"], 'Key': t.key}, ExpiresIn = expiresIn)
    for face in data:
       signedUrl = s3client.meta.client.generate_presigned_url('get_object', Params = {'Bucket': face["bucket"], 'Key': face["key"]}, ExpiresIn = expiresIn)
       face["url"]=signedUrl             
    return data

def deleteFace(faceId):

    faces=[]
    faces.append(faceId)
    rekoclient.delete_faces(CollectionId=conf["awsFaceCollection"],FaceIds=faces)

    dbPiFaces.delete_item(
        Key={
            'faceId': faceId
        }
    )



def search_face(data):
    print("searching face...", data["key"])
    try:
        matchedFace={}
        matched=False
        piFace=None
        response=rekoclient.search_faces_by_image(CollectionId=conf["awsFaceCollection"],
                                    Image={'S3Object':{'Bucket':conf["s3bucket_name"],'Name':data["key"]}},
                                    FaceMatchThreshold=80,
                                    MaxFaces=1)
        faceMatches=response['FaceMatches']
        faceMatches.sort(reverse=True,key=sortKey)

        if(len(faceMatches) > 0):
            matched=True
            matchedFace=faceMatches[0]
            piFace=dbPiFaces.get_item(
                Key={
                    'faceId':matchedFace['Face']['FaceId']
                }
            )['Item']
            #piFace = response['Item']


        return matched,piFace
    except:
       print ("Error in AWS Reko: ", sys.exc_info()[0])                          

def check_for_objects():
    global last_epoch
    global last_upload
    global motionCounter
    while True:
        try:
            _, found_obj,frame = video_camera.get_object(object_classifier)
            if found_obj and (time.time() - last_epoch) > conf["min_motion_window"]:
                
                motionCounter += 1
                print("$$$ object found with motion counter ", motionCounter)
                print("min_motion_frames",conf["min_motion_frames"])
                print("last upload was x seconds ago ",(time.time() - last_upload))
                print("min upload interval ",conf["upload_interval"])
                last_epoch = time.time()
                if motionCounter >= conf["min_motion_frames"] and (time.time() - last_upload) > conf["upload_interval"] :
                    print("$$$ upload")
                    last_upload = time.time()
                    motionCounter = 0
                    t = TempImage()
                    cv2.imwrite(t.path, frame)
                    s3client.meta.client.upload_file(t.path, conf["s3bucket_name"], t.key )
                    signedUrl = s3client.meta.client.generate_presigned_url('get_object', Params = {'Bucket': conf["s3bucket_name"], 'Key': t.key}, ExpiresIn = expiresIn)
                    faceId=None
                    faceName="Visitor"
                    matched = False
                    if conf["use_rekognition"]== True:
                        time.sleep(1)
                        rekodata ={}
                        rekodata["key"]=t.key
                        matched,piFace = search_face(rekodata)
                        if matched == True:
                            faceId = piFace['faceId']
                            faceName = piFace['faceName']

                    slack_data = {
                        'attachments': [
                            {
                                'color': "#36a64f",
                                'pretext': faceName+ " at the front door",
                                'title': "Home Surveillance",
                                'title_link': "https://hss.crazykoder.com",
                                'image_url': signedUrl
                        
                            }
                        ]
                    }
                    requests.post(conf["slack_incoming_webhook"], data=json.dumps(slack_data),headers={'Content-Type': 'application/json'})
                    persistNotification({
                        "id": str(uuid.uuid4()),
                        "createdOn": datetime.now().isoformat(),
                        "bucket": conf["s3bucket_name"],
                        "signedUrl":signedUrl,
                        "key":t.key,
                        "faceId": faceId,
                        "faceName":faceName
                    })
                    t.cleanup()
                    # prompt visitor to leave voice message
                    polly.speak("Hello "+faceName+"....  Please leave your brief message after the beep....")
                    recordGuestVoice()
                    

                else:
                    print("$$$ dont upload")
                
        except:
            print ("Error sending email: ", sys.exc_info()[0])

def persistMessage(Item):
    dbPiMessages.put_item(
        Item=Item
    )   
def persistNotification(Item):
    dbPiNotification.put_item(
        Item=Item
    ) 


@app.route('/')
def index():
    return render_template('index.html', async_mode=socketio.async_mode)

def gen(camera):
    while True:
        frame,_ ,_= camera.get_object(object_classifier)
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')

# @app.after_request
# def apply_caching(response):
#     response.headers.add('Access-Control-Allow-Origin', '*')
#     response.headers.add('Access-Control-Allow-Headers', 'Origin,Content-Type,Authorization')
#     response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
#     response.headers.add('Access-Control-Allow-Credentials', 'true')
#     return response

@app.before_request
def authorize_token():
    
    try:
        if request.method != 'OPTIONS' :  # <-- required
            if request.endpoint!='video_feed':
                auth_header = request.headers.get("Authorization")
                if "Basic" in auth_header:
                    print("Header found")
                    token=auth_header.split(' ')[1]
                    print(token)
                    s = base64.b64decode(token).decode('utf-8').split(':')
                    print(s)
                    username=s[0]
                    password=s[1]

                    if username != 'gungun' and password != 'gungun':
                        raise ValueError('Authorization failed.')
                else:
                    print("No auth reader")
                    raise ValueError('Authorization failed.')
            else:
                token = request.args.get('token')
                s = base64.b64decode(token).decode('utf-8').split(':')
                print(s)
                username=s[0]
                password=s[1]
                if username != 'gungun' and password != 'gungun':
                    raise ValueError('Authorization failed.')        

    except Exception as e:
            return "401 Unauthorized\n{}\n\n".format(e), 401


@app.route('/video_feed')
def video_feed():
    return Response(gen(video_camera),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/api/messages', methods=['GET'])
def api_get_messages():
    data = scanMessages()
    return jsonify(data)

@app.route('/api/messages/<id>/<createdOn>', methods=['DELETE'])
def api_delete_message(id,createdOn):
    deleteMessage(id,createdOn)  
    return jsonify({"success":"true"})

@app.route('/api/notification', methods=['GET'])
def api_get_notification():
    response = dbPiNotification.scan()
    data = response['Items']
    return jsonify(data)

@app.route('/api/notification/<id>/<createdOn>', methods=['DELETE'])
def api_delete_notification(id,createdOn):
    deleteNotification(id,createdOn)  
    return jsonify({"success":"true"})


@app.route('/api/faces', methods=['GET'])
def api_get_faces():
    data = scanFaces()
    return jsonify(data)    

@app.route('/api/faces/<id>', methods=['DELETE'])
def api_delete_face(id):
    deleteFace(id)  
    return jsonify({"success":"true"}) 

@app.route('/api/faces/index', methods=['POST'])
def index_face_route():
    key=request.json["key"]
    faceName=request.json["faceName"]
    id=request.json["id"]
    createdOn=request.json["createdOn"]
    retobject={}
    #copy from slack bucket to face bucket
    copy_source = {
    'Bucket':conf["s3bucket_name"],
    'Key': key
    }
    s3client.meta.client.copy(copy_source, conf["s3bucket_faces"], key)
    response=rekoclient.index_faces(CollectionId=conf["awsFaceCollection"],
                                Image={'S3Object':{'Bucket':conf["s3bucket_faces"],'Name':key}},
                                ExternalImageId=key,
                                MaxFaces=1,
                                QualityFilter="NONE",
                                DetectionAttributes=['ALL'])

    for faceRecord in response['FaceRecords']:
        print('  Face ID: ' + faceRecord['Face']['FaceId'])
        retobject["faceId"]= faceRecord['Face']['FaceId']
        retobject["boundingBox"]= faceRecord['Face']['BoundingBox']

    dbPiFaces.put_item(
        Item={
                'faceId': retobject["faceId"],
                'faceName': faceName,
                'key': key,
                'bucket':conf["s3bucket_faces"],
                'boundingBox':json.dumps(retobject["boundingBox"])
            }
    )
    #update existing notification
    updateNotification(id,createdOn,retobject["faceId"],faceName)

    return jsonify(retobject)

@app.route('/api/faces/search', methods=['POST'])
def search_face_route():
    _,matchedFace = search_face(request.json)   
    return  jsonify(matchedFace)


@socketio.on('connect', namespace='/test')
def test_connect():
    token = request.args.get('token')
    print("socket token ", token)
    

@socketio.on('disconnect', namespace='/test')
def test_disconnect():
    print('Client disconnected')

def recordGuestVoice():
    polly.playBeep()
    time.sleep(1)
    try:
        polly.record()
    except:
        pass    
    print("recoding done!")
    id=str(uuid.uuid4())
    key=id+".wav"
    s3client.meta.client.upload_file('./request.wav', conf["s3bucket_voice"], key)
    signedUrl = s3client.meta.client.generate_presigned_url('get_object', Params = {'Bucket': conf["s3bucket_voice"], 'Key': key}, ExpiresIn = expiresIn)
    Item2={
            "id": id,
            "createdOn": datetime.now().isoformat(),
            "audio": signedUrl,
            "type": "voice",
            "source": "guest"
    }
    
    persistMessage(Item2)
    print("voice message persisted")
    socketio.emit('guest_event', Item2,namespace='/test')
    print("guest event sent")
    

@socketio.on('owner_event', namespace='/test')
def test_message(message):
    print(message['data'])
    polly.speak(message['data']+"... after the beep please leave your message...")
    #time.sleep(2)
    Item={
            "id": str(uuid.uuid4()),
            "createdOn": datetime.now().isoformat(),
            "message": message['data'],
            "type": "text",
            "source": "owner"
    }
    persistMessage(Item)
    recordGuestVoice()

if __name__ == '__main__':
    t = threading.Thread(target=check_for_objects, args=())
    t.daemon = True
    t.start()
    #app.run(host='0.0.0.0', debug=False)
    socketio.run(app,host='0.0.0.0', debug=False)
    #socketio.run(app)