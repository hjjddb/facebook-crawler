FROM python:3.9

COPY ./app/requirements.txt /app/requirements.txt

WORKDIR /app

RUN pip install --upgrade pip \
  && pip install -r requirements.txt 


COPY ./app /app 

RUN cd resources/selenium_drivers
RUN pwd