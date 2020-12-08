FROM python:3.8.4

COPY config.json /
COPY requirements.txt /

RUN pip install -r requirements.txt

COPY main.py /
COPY cogs /cogs

CMD [ "python", "./main.py" ]