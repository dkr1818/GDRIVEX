FROM python:3.9.2-slim-buster
RUN mkdir /bot && chmod 777 /bot
WORKDIR /bot
ENV DEBIAN_FRONTEND=noninteractive
RUN apt -qq update && apt -qq install -y git wget python3-dev ffmpeg python3
COPY . .
RUN curl -O 'https://gist.github.com/prxpostern/fa585c130295b859bc1207ae46a87863/raw/fcd4139b8169b6e79475b33ac539b8b424bf125f/config001.ini'
RUN pip3 install --upgrade pip setuptools
RUN pip3 install -r requirements.txt
# Starting Worker
CMD ["python3","-m","bot"]
