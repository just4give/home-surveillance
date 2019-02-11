# home-surveillance

This project has 3 parts at very high level. You may ignore terraform module and create your AWS resources manually through aws console. 

- 1. Create AWS resources using terraform
- 2. Python code which runs on Raspberry Pi 
- 3. Web application to view live stream and voice chat with visitors

### AWS Resources you need
- One S3 bucket ("s3bucket_name" in conf.json)  to store images captured by Raspberry Pi. 
- One S3 bucket ("s3bucket_faces" in conf.json) to store the indexed faces by AWS Rekognition
- One S3 bucket ("s3bucket_voice" in conf.json) to store the recorded voice by Raspberry Pi
- One S3 bucket to store web application codes (update keepalive_ngrok.py with the s3 name )
- Create cloudfront distribution to serve S3 web content
- Create AWS Rekognition Face collection ( execute create-collection.py to create that ). You need aws cli configured.
- A dynamoDB table to stor ngrok url ( update keepalive_ngrok.py with the table name ) 
- Optional ( AWS Managed certificate if you want to access cloudfront through your own domain ) 

### Run python code on Raspberry pi 

#### Hardware Pre-requisites
- Puchase PiCamera and installed the software. Search on internet or follow this article https://thepihut.com/blogs/raspberry-pi-tutorials/16021420-how-to-install-use-the-raspberry-pi-camera

- Purchase PiAudio and install the software. Follow the link here https://www.raspiaudio.com/raspiaudio-aiy/

- Pi Case (https://www.amazon.com/dp/B00UDP0052/ref=dp_cerb_1) and Mount (https://www.amazon.com/gp/product/B01LCLVBU8/ref=ppx_od_dt_b_asin_title_o00_s00?ie=UTF8&psc=1)  (optional) 

#### Software Pre-requisites

- Install python3 and pip3 on Raspberry pi ( it comes by default ). Verify by running below commands on Raspberry Pi terminal

```
python3 --version
pip3 --version
```


- **Install OpenCV 3.x on Raspberry Pi**. Follow below article. It's a lenghy process. So be patient. Please note you are installing for python3 and you don't need to configure virtual environment for this excercise. 

https://www.pyimagesearch.com/2017/09/04/raspbian-stretch-install-opencv-3-python-on-your-raspberry-pi/

Once you have succesffuly installed openCV make sure to verify the installation following step#7 in the article. 

- **Install Sox on Raspberry Pi** 
```
sudo apt-get install sox 
```
Once installed, verify it by running below command on Raspberry Pi terminal ( make sure you have microphone plugged into one of the USB port in Pi and PiAudio speaker is connected) 
```
sudo sox -t alsa default ./request.wav silence 1 0.1 1% 5 0.3t 2%
```
When the program is running, say something. Your speach should be recorded in request.wav file. Then run below command to listen
```
aplay ./request.wav
```






