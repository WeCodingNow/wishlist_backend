FROM python:3.7-alpine
WORKDIR /authserver
COPY . /authserver
RUN pip install -r requirements.txt
CMD ["python3", "authserver.py"]
