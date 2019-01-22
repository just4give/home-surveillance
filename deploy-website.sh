cd website && npm run build

aws s3 cp ./dist s3://homesurveillance-client-website.prod  --recursive 

aws cloudfront create-invalidation --distribution-id E1C4CV5OVFP0PA --paths "/*"

