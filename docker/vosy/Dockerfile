FROM python:2.7       
COPY . /code

EXPOSE 5001

WORKDIR /code

RUN pip install -r requirements.txt

# ENV HOST_IP '0.0.0.0'

ENTRYPOINT python vosy_app/vosy.py --host $HOST_IP