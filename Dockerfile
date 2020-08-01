FROM python:3.6

ADD stock-RESTClient.py /
ADD requirements.txt /
ADD lib /lib

VOLUME /database

RUN pip install -r requirements.txt

CMD ["python", "stock-RESTClient.py"]

EXPOSE 5000/tcp
