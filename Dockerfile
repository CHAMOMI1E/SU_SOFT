FROM python:3.12-alpine

LABEL authors="chamomile"


WORKDIR /SU_SOFT



COPY ./requirements.txt ./

RUN pip install --upgrade pip

RUN pip install --no-cache-dir -r ./requirements.txt

COPY ./ ./



RUN chmod -R 777 ./