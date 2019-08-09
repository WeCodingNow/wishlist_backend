FROM python:3.7-alpine
WORKDIR /crawler
COPY . /crawler
RUN pip install -r requirements.txt
CMD ["python3", "crawler.py"]
# COPY requirements.txt requirements.txt
