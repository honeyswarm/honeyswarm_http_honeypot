FROM python:3.8.2-buster

ADD honeypot /opt/honeypot
WORKDIR /opt/honeypot

RUN pip install --no-cache-dir -r /opt/honeypot/requirements.txt

CMD ["python", "./app.py"]

