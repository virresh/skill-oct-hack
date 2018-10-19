cd /home/viresh/.virtualenvs/alexaenv/lib/python3.6/site-packages/
zip -X -r /mnt/Common/Hackathons/Alexa_OctSkillHack/pack.zip *
cd /mnt/Common/Hackathons/Alexa_OctSkillHack/lambda_code
zip -X -r /mnt/Common/Hackathons/Alexa_OctSkillHack/pack.zip *
echo "Zip file Created. Uploading to S3 bucket."
aws s3 mb s3://interviewme-bucket --region us-east-1
echo "Bucket Created. Uploading to bucket."
aws s3 cp /mnt/Common/Hackathons/Alexa_OctSkillHack/pack.zip s3://interviewme-bucket/pack.zip
echo "Uploaded to Bucket. Loading to lambda."
aws lambda update-function-code --function-name interviewMe --region us-east-1 --s3-bucket interviewme-bucket --s3-key pack.zip
echo "Uploaded to lambda."
aws s3 rb s3://interviewme-bucket --force
echo "Push Success !"
