FROM public.ecr.aws/lambda/python:3.11
COPY ./src/requirements.txt ./
RUN pip3 install --no-cache-dir --upgrade pip
RUN pip3 install --no-cache-dir -r ./requirements.txt
COPY lambda_function.py ./

CMD [ "lambda_function.lambda_handler" ]