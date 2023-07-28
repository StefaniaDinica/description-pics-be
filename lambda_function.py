import serverless_wsgi
from app import app
import logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

def lambda_handler(event, context):
    return serverless_wsgi.handle_request(app, event, context)