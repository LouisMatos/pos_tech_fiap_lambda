FROM public.ecr.aws/lambda/python:3.10
COPY ./src/requirements.txt .
RUN  pip3 install -r requirements.txt --target "${LAMBDA_TASK_ROOT}"
COPY . ${LAMBDA_TASK_ROOT}
CMD ["app.lambda_handler"]