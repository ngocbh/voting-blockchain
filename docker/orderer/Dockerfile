FROM python:2.7       
COPY . /code
EXPOSE 5001

WORKDIR /code

RUN pip install -r requirements.txt

ENTRYPOINT python bcb_server/orderer.py