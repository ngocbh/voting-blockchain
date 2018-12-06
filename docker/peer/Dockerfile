FROM python:2.7       
ADD . .
EXPOSE 5001

RUN pip install -r requirements.txt

# ENV ORDERER_IP '0.0.0.0'
# ENV CA_IP '0.0.0.0'


WORKDIR /bcb_server
ENTRYPOINT python peer.py --ca $CA_IP --orderer $ORDERER_IP