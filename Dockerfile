# base image
FROM python:slim

# set working directory
WORKDIR /data
# Add requirements and py-files
COPY requirements.txt main.py calculation.py /data/
COPY templates /data/templates/
COPY project /data/project/

# Add cronjob to delete files after one week
COPY cron_del_files /etc/cron.d/cron_del_files
RUN apt-get update && apt-get -y install cron
RUN chmod 0644 /etc/cron.d/cron_del_files && \
    crontab /etc/cron.d/cron_del_files && \
    cron

# install numpy and requirements
RUN bash -c 'mkdir -p /data/{files,zipped}' && \
    # Numpy not necessary because it's pulled with biopython?
    #pip install numpy && \
    pip install -r requirements.txt
