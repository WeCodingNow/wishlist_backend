FROM python:3.7-alpine
WORKDIR /apiserver
COPY . /apiserver

RUN apk add --no-cache --virtual .build-deps gcc musl-dev

RUN pip install -r requirements.txt

CMD ["python3", "ourAPI.py"]

# EXPOSE 8080
