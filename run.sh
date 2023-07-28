echo 'Building docker image...'
docker build -t pics-ml .
echo 'Creating tag...'
docker tag pics-ml:latest 880694716580.dkr.ecr.eu-west-1.amazonaws.com/stefania-repo:latest
echo 'Pushing to ECR...'
docker push 880694716580.dkr.ecr.eu-west-1.amazonaws.com/stefania-repo:latest
echo 'Done'