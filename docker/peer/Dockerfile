FROM python:2.7       
COPY . /code
EXPOSE 5001

WORKDIR /code

RUN pip install -r requirements.txt

# ENV ORDERER_IP '0.0.0.0'
# ENV CA_IP '0.0.0.0'

ENTRYPOINT python bcb_server/peer.py --ca $CA_IP --orderer $ORDERER_IP