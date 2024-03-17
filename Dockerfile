#FROM public.ecr.aws/lambda/python:3.10
#COPY requirements.txt .
#RUN  pip3 install -r requirements.txt --target "${LAMBDA_TASK_ROOT}"
#COPY . ${LAMBDA_TASK_ROOT}
#CMD ["app.lambda_handler"]


FROM public.ecr.aws/lambda/python:3.9
#RUN pip install --upgrade pip
COPY ./src/requirements.txt ./
RUN pip3 install --upgrade pip
RUN pip3 install -r ./requirements.txt
COPY lambda_function.py ./

CMD [ "lambda_function.lambda_handler" ]