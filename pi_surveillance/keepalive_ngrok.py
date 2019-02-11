
import json
import subprocess
import time
from pathlib import Path
import atexit
import boto3
import requests
import datetime


#ngrokDir="/Users/mithun.das/Downloads"
ngrokDir="/home/pi"
deviceId="camporch"
prodBucket="homesurveillance-client-website.prod"
dynamodb = boto3.resource('dynamodb')
dbPiNgRok = dynamodb.Table('PiNgRok')
s3client = boto3.resource('s3')
localhost_url = "http://localhost:4040/api/tunnels"  # Url with tunnel details

def updateDynamoDB(ngrok_address):
    dbPiNgRok.update_item(
        Key ={
            'deviceId': deviceId
        },
        UpdateExpression='SET address = :address, createdOn=:createdOn',
        ExpressionAttributeValues={
            ':address': ngrok_address,
            ':createdOn': '{:%Y-%m-%d %H:%M:%S}'.format(datetime.datetime.now())
        }
    )

def is_running():
    try:
        ngrok_req = requests.get(localhost_url).text
        ngrok_address = get_ngrok_url(ngrok_req)
        print("ngrok is already running {ngrok_address}".format(ngrok_address=ngrok_address))
        #check if expired
        r=requests.get(ngrok_address)
        if r.status_code == 402:
            return _run_ngrok()
        return ngrok_address
    except Exception as e: 
        print("exception",e)
        return _run_ngrok()

def get_ngrok_url(ngrok_req):
    j = json.loads(ngrok_req)
    tunnel_url = j['tunnels'][len(j['tunnels'])-1]['public_url']  # Do the parsing of the get
    #tunnel_url = tunnel_url.replace("http", "https")
    return tunnel_url


def _run_ngrok():
    global ngrokDir
    command = "ngrok"
    executable = str(Path(ngrokDir, command))
    ngrok = subprocess.Popen([executable, 'http', '-inspect=false','-bind-tls=true', '5000'])
    atexit.register(ngrok.terminate)
    time.sleep(3)
    tunnel_url = requests.get(localhost_url).text  # Get the tunnel information
    ngrok_address =get_ngrok_url(tunnel_url)
    print("ngrok created  {ngrok_address}".format(ngrok_address=ngrok_address))
    updateDynamoDB(ngrok_address)
    with open('config.json', 'w') as outfile:
        json.dump({
            "serverUrl":ngrok_address,
            "production": "true",
            "supportedLanguages": ["en-US", "fr-FR"],
            "defaultLanguage": "en-US"}, outfile)
    s3client.meta.client.upload_file('config.json', prodBucket, 'assets/config.json' )
    #subprocess.call("aws cloudfront create-invalidation --distribution-id E1C4CV5OVFP0PA --paths '/*'",shell=True) 
    time.sleep(3450) # keep the process running for 3450 seconds
    return ngrok_address


#ngrok_address=start_ngrok()
#print(ngrok_address)
is_running()
