# home-surveillance

**Please note, this project has many floating parts and I built it over time. So there is a chance I missed some steps in this readme. Please be patient and apply your debug skill to investigate the issues or log issues in this repo. I will try to work with you to resolve those**

![hss_coversheet](https://user-images.githubusercontent.com/9275193/52678665-70c56180-2f00-11e9-8038-e6f898834cda.jpg)

Watch live demo on youtube 

https://youtu.be/SWP4vH6JPDw



This project has 3 parts at very high level. You may ignore terraform module and create your AWS resources manually through aws console. 

- Create AWS resources using terraform
- Python code which runs on Raspberry Pi 
- Web application to view live stream and voice chat with visitors

### AWS Resources you need
- One S3 bucket ("s3bucket_name" in conf.json)  to store images captured by Raspberry Pi. 
- One S3 bucket ("s3bucket_faces" in conf.json) to store the indexed faces by AWS Rekognition
- One S3 bucket ("s3bucket_voice" in conf.json) to store the recorded voice by Raspberry Pi
- One S3 bucket to store web application codes (update keepalive_ngrok.py with the s3 name )
- Create cloudfront distribution to serve S3 web content
- Create AWS Rekognition Face collection ( execute create-collection.py to create that ). You need aws cli configured.
- A dynamoDB table to stor ngrok url ( update keepalive_ngrok.py with the table name ) 
- Optional ( AWS Managed certificate if you want to access cloudfront through your own domain ) 

## Run python code on Raspberry pi 

### Hardware Pre-requisites
- Puchase PiCamera and installed the software. Search on internet or follow this article https://thepihut.com/blogs/raspberry-pi-tutorials/16021420-how-to-install-use-the-raspberry-pi-camera

- Purchase PiAudio and install the software. Follow the link here https://www.raspiaudio.com/raspiaudio-aiy/

- Pi Case (https://www.amazon.com/dp/B00UDP0052/ref=dp_cerb_1) and Mount (https://www.amazon.com/gp/product/B01LCLVBU8/ref=ppx_od_dt_b_asin_title_o00_s00?ie=UTF8&psc=1)  (optional) 

### Software Pre-requisites

- Install python3 and pip3 on Raspberry pi ( it comes by default ). Verify by running below commands on Raspberry Pi terminal

```
python3 --version
pip3 --version
```
- **Install and configure AWS CLI**
```
sudo pip3 install awscli
sudo aws configure
```
For this tutorial start with an IAM user with Admin access to avoid some permission issues. Once everything is setup you may restrict some access as needed.

- **Install OpenCV 3.x on Raspberry Pi**. Follow below article. It's a lenghy process. So be patient. Please note you are installing for python3 and you don't need to configure virtual environment for this excercise. 

https://www.pyimagesearch.com/2017/09/04/raspbian-stretch-install-opencv-3-python-on-your-raspberry-pi/

Once you have succesffuly installed openCV make sure to verify the installation following step#7 in the article. 

- **Install Sox on Raspberry Pi** 
```
sudo apt-get update
sudo apt-get install sox 
```
After this copy .asoundrc file to root directory and verify Sox by running below command on Raspberry Pi terminal ( make sure you have microphone plugged into one of the USB port in Pi and PiAudio speaker is connected) 
```
sudo sox -t alsa default ./request.wav silence 1 0.1 1% 5 0.3t 2%
```
When the program is running, say something. Your speach should be recorded in request.wav file. Then run below command to listen
```
aplay ./request.wav
```
- **Install Ngrok** 

Follow this article http://crazykoder.com/2019/01/28/keep-ngrok-running-forever-on-raspberry-pi/ to download and setup Ngrok. Please copy keepalive_ngrok.py and .sh file from this repo instead of the above link. Note everytime this script is run it will update /assets/config.json file in your S3 bucket where your web application code is hosted. 

- **Create slack webhook**

We are using Slack to get notified when someone appears in front of the camera. Your Pi will detect the face and send the image to the slack channel. Please follow this article to generate slack webhook and update the webhook url in conf.json file. If you want to get notified via email or anything else, you can do so. You need to modify the main.py and have your own implementation.

https://get.slack.help/hc/en-us/articles/115005265063-Incoming-WebHooks-for-Slack



- **Update config**

Now copy all the files and folders from pi_suveillance folder to /pi/home/home_surveillance folder. Then cd into /pi/home/home_surveillance , update config.json file with your AWS resources name. Choose username and passowrd and execute below command
```
sudo pip3 install imutils boto3 flask Flask-BasicAuth flask_socketio psutil flask_cors
sudo python3 main.py
```
First time you may get bunch of errors complaining about missing modules. Use suod pip3 to install missing modules. Your app should be running on port 5000. 

## Run Angular Web 
Before you deploy your code to AWS Cloud, run it on local and make sure it's able to connect to your Raspberry Pi ( make sure your computer and Pi on same Wifi ) 

cd into website folder. Then update src/assets/config.json file. Change serverUrl to http://<your_pi_ip_address>:5000 
Then issue below command on your computer terminal 

```
npm install && npm start
```
This should build and start your wen application on port 4200. Open your browser and hit the url. It should ask for login. Use the same username and passowrd you used in python conf.json file. You should be able to see live stream from your Raspberry Pi



## Deploy UI code
if you have cloudfront and S3 bucket setup to host you web application then open deploy-website.sh. Change S3 bucket name and cloudfront distribution id and then issue below command
```
sh deploy-website.sh
```




