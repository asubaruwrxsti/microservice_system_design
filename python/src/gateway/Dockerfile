FROM --platform=linux/amd64 python:3.10-slim-bullseye as build
RUN apt-get update \
	&& apt-get install -y --no-install-recommends --no-install-suggests \
	pkg-config python3-dev build-essential default-libmysqlclient-dev \
	&& pip install --no-cache-dir --upgrade pip 

WORKDIR /app
COPY requirements.txt /app
RUN pip install --no-cache-dir --requirement /app/requirements.txt
COPY . /app

EXPOSE 8080

CMD ["python3", "server.py"]