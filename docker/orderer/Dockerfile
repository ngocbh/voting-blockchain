FROM python:2.7       
COPY . .
EXPOSE 5001
RUN pip install -r requirements.txt

WORKDIR /bcb_server
ENTRYPOINT python orderer.py