# description.pics backend

This project aims to provide an API for helping with files uploading and description generating.

The deployed web application can be viewed at https://description.pics.

Medium post: [Multi-label classification for generating images descriptions](https://medium.com/@stefaniadinica/multi-label-classification-for-generating-images-descriptions-8f362fe5dff8)

## Project structure
```
├── app.py
├── lambda_function.py
├── Dockerfile
├── labels.npy
├── README.md
├── requirements.txt
├── model-image-description.h5
├── run.sh
```

The structure of this project was made in order to be deployed on AWS lambda using a docker container. Do not change the structure!

## About the files
- app.py - flask backend

In app.py, if needed, update WIDTH and HEIGHT variables with the ones used for training the model.
- lamba_function.pt - entrypoint in AWS lambda
- Dockerfile - is the file used for creating the Docker image
- run.sh - script for creating the Docker image and uploading it to AWS ECR
- model-image-description.h5 - is not uploaded to git because it's a large file. Download it from https://drive.google.com/drive/folders/1LcARea0fQz4y9lul623hvzDLuXBrDcN0?usp=drive_link.
- labels.npy - the array of labels

## Endpoints (app.py)
- GET /api/get-upload-url: requests a presigned url from S3, for 'pics-ml' bucket and returns it
- GET /api/get-upload-url-no-descr: requests a presigned url from S3, for 'pics-generate-description' bucket and returns it
- POST /api/add-image-info: adds a new entry (image description) to 'PicsDetails' table in Dynamo DB
- GET /api/generate-description: loads the model, predicts the description for the requested file and returns the top 3 predicted labels

