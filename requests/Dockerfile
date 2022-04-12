# base image
FROM python:slim-jessie

# set working directory
WORKDIR /data
# Add requirements and py-files
#COPY requirements.txt main.py calculation.py /data/
COPY ./requests/requirements.txt ./requests/calculation.py /data/
COPY ./requests/main.py /data/
COPY ./requests/templates /data/templates/
COPY ./requests/project /data/project/

# Add cronjob to delete files after one week
COPY ./requests/cron_del_files /etc/cron.d/cron_del_files
RUN apt-get update && apt-get -y install cron && \
    apt-get -y install gcc
RUN chmod 0644 /etc/cron.d/cron_del_files && \
    crontab /etc/cron.d/cron_del_files && \
    cron
# Add API Key from .env file to the Docker container env variables
ARG BACKEND_APIKEY
ENV BACKEND_APIKEY=${BACKEND_APIKEY}

# Set array lenghts and counts for MAFFT and ClustalW calculations
ARG MAFFT_ARRAY_COUNT
ARG MAFFT_ARRAY_LENGTH
ARG CLUSTALW_ARRAY_COUNT
ARG CLUSTALW_ARRAY_LENGTH
ARG NO_ALIGNMENT_ARRAY_COUNT
ARG NO_ALIGNMENT_ARRAY_LENGTH
ENV MAFFT_ARRAY_COUNT=${MAFFT_ARRAY_COUNT}
ENV MAFFT_ARRAY_LENGTH=${MAFFT_ARRAY_LENGTH}
ENV CLUSTALW_ARRAY_COUNT=${CLUSTALW_ARRAY_COUNT}
ENV CLUSTALW_ARRAY_LENGTH=${CLUSTALW_ARRAY_LENGTH}
ENV NO_ALIGNMENT_ARRAY_COUNT=${NO_ALIGNMENT_ARRAY_COUNT}
ENV NO_ALIGNMENT_ARRAY_LENGTH=${NO_ALIGNMENT_ARRAY_LENGTH}
ENV PYTHONUNBUFFERED=1
# Added so that main.py can import calculation.py 
ENV PYTHONPATH=/data
ENV APP_SETTINGS=project.server.config.DevelopmentConfig

# install numpy and requirements
RUN bash -c 'mkdir -p /data/{files,zipped}' && \
    pip install -r requirements.txt
