FROM python:3.11.2-bullseye AS app

WORKDIR /app

COPY requirements.txt ./

RUN pip3 install -r requirements.txt

COPY static/ ./static
COPY collocations_new.csv ./
COPY correct.csv ./
COPY dictionary_2.csv ./
COPY server.py ./
COPY gunicorn.py.ini ./


EXPOSE 8000

CMD ["gunicorn", "-c", "gunicorn.py.ini", "server:app"]