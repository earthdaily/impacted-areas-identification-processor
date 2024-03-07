
FROM continuumio/miniconda3:23.10.0-1
EXPOSE 80

RUN pip install --upgrade pip==22.0.4
RUN conda clean --all
RUN pip cache purge

WORKDIR /app

COPY ./requirements.txt .
RUN pip install -r requirements.txt
RUN pip cache purge; exit 0
RUN apt-get update && apt-get install -y dos2unix
COPY ./src .
COPY .env .

COPY docker-entrypoint.sh /usr/local/bin/
RUN dos2unix /usr/local/bin/docker-entrypoint.sh
RUN chmod +x /usr/local/bin/docker-entrypoint.sh

ENTRYPOINT ["docker-entrypoint.sh"]
