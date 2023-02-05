FROM python:3.8.16-bullseye

COPY requirements.txt /requirements.txt
RUN  python -m pip install --upgrade pip && pip install -U setuptools
RUN  python -m pip install -r ./requirements.txt 

WORKDIR /app
COPY . /app

CMD [ "gunicorn", "app:serve", "--bind", "0.0.0.0:8080", "--worker-class", "aiohttp.GunicornWebWorker",]
      