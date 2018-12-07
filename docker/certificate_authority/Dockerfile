FROM python:2.7       
COPY . /code
EXPOSE 5001

WORKDIR /code

RUN pip install -r requirements.txt

# ENV ORDERER_IP '0.0.0.0'

ENTRYPOINT python bcb_server/certificate_authority.py --orderer $ORDERER_IP