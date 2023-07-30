from flask import Flask, request, jsonify
import logging
import boto3
import uuid
import datetime
from botocore.exceptions import ClientError
from flask_cors import CORS, cross_origin
import tensorflow as tf
from keras.preprocessing import image
from PIL import Image
import io
import numpy as np
import pandas as pd
import json

logger = logging.getLogger()
logger.setLevel(logging.INFO)
logging.getLogger('flask_cors').level = logging.DEBUG
handler = logging.StreamHandler()
handler.setFormatter(logging.Formatter(
    ">>>>>>:%(levelname)s<<<<<<:%(message)s"))
logger.setLevel(logging.INFO)
logger.addHandler(handler)

#These values must be replaced with the minimum width and height of the images (in pixels)
WIDTH = 367
HEIGHT = 400

app = Flask(__name__)

def getTopLabels(pred, all_tokens, num_labels):
    '''Reads data from the database and loads it into dataframes

    Args:
    pred (array of numbers) - a predicted array of 0's and 1's,
    all_tokens (array of strings) - an array of labels,
    num_labels (number) - the number of labels to return 

    Returns:
    labels (array of strings) - the top num_labels labels;
    values (array of floats) - the predicted values for the labels
    '''
    df = pd.DataFrame(columns=all_tokens)
    df.loc[0] = pred[0]

    labels = list(df.iloc[:, np.argsort(df.loc[0])].columns[-num_labels:])
    labels.reverse()
    values = list(df.iloc[0, np.argsort(df.loc[0])][-num_labels:])
    values.reverse()

    return labels, values


@app.route('/api/get-upload-url')
def getUploadUrl():
    '''Gets a presigned url from pics-ml bucket in S3 and returns it
    '''
    s3_client = boto3.client('s3')
    try:
        response = s3_client.generate_presigned_post(
            'pics-ml', str(uuid.uuid4()), Conditions=[["content-length-range", 0, 15728640]], ExpiresIn=3600)
    except ClientError as err:
        logger.error("Couldn't generate presigned url2. Here's why: %s: %s",
                     err.response['Error']['Code'], err.response['Error']['Message'])
        raise

    # The response contains the presigned URL
    return response


@app.route('/api/get-upload-url-no-descr')
def getUploadUrlNoDescr():
    '''Gets a presigned url from pics-generate-description bucket in S3 and returns it
    '''
    s3_client = boto3.client('s3')
    try:
        response = s3_client.generate_presigned_post('pics-generate-description', str(
            uuid.uuid4()), Conditions=[["content-length-range", 0, 15728640]], ExpiresIn=3600)
    except ClientError as err:
        logger.error("Couldn't generate presigned url2. Here's why: %s: %s",
                     err.response['Error']['Code'], err.response['Error']['Message'])
        raise

    # The response contains the presigned URL
    return response


@app.route('/api/generate-description')
def generateDescription():
    '''Gets an image from S3, loads the model, predicts the description for the image
    and returns it
    '''
    args = request.args
    id = args.get("id")

    s3_client = boto3.client('s3')
    bucket = 'pics-generate-description'

    try:
        data = s3_client.get_object(Bucket=bucket, Key=id)
        contents = data['Body'].read()

        img_pred = Image.open(io.BytesIO(contents))
        img_pred = img_pred.convert('RGB')
        img_pred = image.img_to_array(img_pred)
        img_pred = img_pred / 255
        img_pred = np.resize(img_pred, (WIDTH, HEIGHT, 3))
        img_pred.shape

        logger.info('Reading model...')

        # Recreate the exact same model, including its weights and the optimizer
        new_model = tf.keras.models.load_model('./model-image-description.h5')

        # Show the model architecture
        new_model.summary()

        # Predict
        pred = new_model.predict(np.array([img_pred]))

        labels = np.load('./labels.npy')
        labels, values = getTopLabels(pred, labels, 3)

        response = {
            'labels': labels,
            'values': values
        }

        json_object = json.dumps(response, indent=4)
    except ClientError as err:
        logger.error(ClientError)
        raise

    # The response contains the presigned URL
    return json_object


@app.route('/api/add-image-info',  methods=["POST"])
def addImageInfo():
    '''Saves image info to Dynamo DB
    '''
    id = request.json['id']
    description = request.json['description']
    name = request.json['name']

    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table('PicsDetails')

    try:
        table.put_item(
            Item={
                "Id": id,
                "UploadDate": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "Description": description,
                "Name": name
            },
            ConditionExpression="#id <> :id",
            ExpressionAttributeNames={
                "#id": "Id"
            },
            ExpressionAttributeValues={
                ":id": id
            }
        )
    except ClientError as err:
        if err.response['Error']['Code'] == 'ConditionalCheckFailedException':
            return "This was not a unique key"
        logger.error("Couldn't add pics id %s to table PicsDetails. Here's why: %s: %s",
                     id, err.response['Error']['Code'], err.response['Error']['Message'])
        raise
    return "seccess"


if __name__ == '__main__':
    app.run(threaded=False)
