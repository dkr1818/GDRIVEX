FROM python:3.9.2-slim-buster

WORKDIR /root/bot

COPY . .

RUN pip3 install --upgrade pip setuptools

RUN pip3 install -r requirements.txt

# Starting Worker
CMD ["python3","-m","bot"]
