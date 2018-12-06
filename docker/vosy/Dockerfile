FROM python:2.7       
ADD . .

EXPOSE 5001
RUN pip install -r requirements.txt

# ENV HOST_IP '0.0.0.0'

WORKDIR /vosy_app
ENTRYPOINT python vosy.py --host $HOST_IP