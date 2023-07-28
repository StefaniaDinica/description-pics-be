FROM public.ecr.aws/lambda/python:3.10

# Copy requirements.txt
COPY requirements.txt ${LAMBDA_TASK_ROOT}

# Copy function code
COPY lambda_function.py ${LAMBDA_TASK_ROOT}
COPY app.py ${LAMBDA_TASK_ROOT}
COPY model-image-description.h5 ${LAMBDA_TASK_ROOT}
COPY labels.npy ${LAMBDA_TASK_ROOT}

RUN pip install --upgrade pip

# Install the specified packages
RUN pip install -r requirements.txt --target "${LAMBDA_TASK_ROOT}"

# Set the CMD to your handler (could also be done as a parameter override outside of the Dockerfile)
CMD [ "lambda_function.lambda_handler" ]
