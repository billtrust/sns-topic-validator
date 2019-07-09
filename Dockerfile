FROM python:3.7 

ENV NODE_VERSION=8.10.0
ENV NVM_DIR=/root/.nvm

RUN \
  apt update && \
  apt install -y wget
RUN \
  wget -qO- https://deb.nodesource.com/setup_8.x | bash - && \
  apt install nodejs && \
  rm -rf /var/lib/apt/lists/*

# COPY ./requirements.txt .
# RUN pip install -r requirements.txt -t . && \

RUN npm install -g serverless

WORKDIR /src

COPY . .

ENV PYTHONUNBUFFERED=1
ENV PYTHONIOENCODING=utf8

ENTRYPOINT ["sls", "invoke", "local", \
            "-f", "sns-topic-validator", \ 
            "--deployBucket", "notneededforinvoke"]
