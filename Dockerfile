FROM python:3.7.3-alpine

RUN apk add --update nodejs npm bash jq && \
    npm install -g serverless && \
    pip3 install boto3 python-jenkins awscli

RUN mkdir -p /package
RUN mkdir -p /app
WORKDIR /app

# tell node where to find dependencies (they are not installed in the normal location)
ENV NODE_PATH /package/node_modules

# install the dependencies
COPY package.json /package/package.json
RUN npm install --prefix /package

# copy the application
COPY . /app
