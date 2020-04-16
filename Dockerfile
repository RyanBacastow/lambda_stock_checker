FROM python:3.7.3
MAINTAINER Ryan Bacastow <ryan.bacastow@tmsw.com>

RUN apt-get update && apt-get install -y gnupg

RUN mkdir -p /app
RUN mkdir -p /local_files
WORKDIR /app
COPY requirements.txt requirements.txt
RUN pip install --upgrade setuptools
RUN pip install --no-cache-dir -r requirements.txt
COPY . .

CMD python ./app.py