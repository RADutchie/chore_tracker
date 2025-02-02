FROM python:3.13-slim

RUN apt-get update && apt-get install -y sqlite3

# set working directory
RUN mkdir -p /usr/src/app
RUN mkdir -p /usr/src/app/data
WORKDIR /usr/src/app

# add requirements
COPY ./requirements.txt /usr/src/app/requirements.txt

# install requirements
RUN pip install -r requirements.txt

# add app
COPY . /usr/src/app

VOLUME /usr/src/app/data

# Expose port for Flask app
EXPOSE 5005

RUN chmod +x prod_entrypoint.sh

# run server
#CMD ["./entrypoint.sh"]
CMD ["./prod_entrypoint.sh"]
