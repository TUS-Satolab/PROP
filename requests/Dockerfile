# base image
FROM python:slim-jessie

# set working directory
WORKDIR /data
# Add requirements and py-files
#COPY requirements.txt main.py calculation.py /data/
COPY requirements.txt calculation.py /data/
COPY templates /data/templates/
COPY project /data/project/

# Add cronjob to delete files after one week
COPY cron_del_files /etc/cron.d/cron_del_files
RUN apt-get update && apt-get -y install cron && \
    apt-get -y install gcc
RUN chmod 0644 /etc/cron.d/cron_del_files && \
    crontab /etc/cron.d/cron_del_files && \
    cron

# Added so that main.py can import calculation.py 
ENV PYTHONPATH=/data

# install numpy and requirements
RUN bash -c 'mkdir -p /data/{files,zipped}' && \
    pip install -r requirements.txt
