#!/bin/sh
python3 /home/pi/keepalive_ngrok.py >> /home/pi/keepalive_ngrok.log 
sleep 10
aws cloudfront create-invalidation --distribution-id E1C4CV5OVFP0PA --paths '/*'

