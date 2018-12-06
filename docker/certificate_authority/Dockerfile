FROM python:2.7       
COPY . .
EXPOSE 5001
RUN pip install -r requirements.txt

WORKDIR /bcb_server

# ENV ORDERER_IP '0.0.0.0'

ENTRYPOINT python certificate_authority.py --orderer $ORDERER_IP