FROM continuumio/miniconda3:4.10.3 
EXPOSE 80
RUN pip install --upgrade pip==23.1.2
RUN pip cache purge 


COPY ./requirements.txt .
RUN pip install -r requirements.txt
RUN pip cache purge; exit 0

COPY ./src .
COPY ./setup.py .
COPY ./.env .

ENTRYPOINT ["hypercorn", "main:app", "-b", "0.0.0.0:80", "--worker-class", "trio"]