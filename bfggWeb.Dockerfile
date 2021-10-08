FROM node

WORKDIR /opt/bfgg-web

COPY ./bfgg-site .
RUN npm install
