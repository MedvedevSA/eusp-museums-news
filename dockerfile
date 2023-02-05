FROM python:3.8.16-bullseye

COPY requirements.txt /requirements.txt
RUN  python -m pip install --upgrade pip && pip install -U setuptools
RUN  python -m pip install -r ./requirements.txt 

WORKDIR /app
COPY . /app

CMD [ "python", "-m aiohttp.web", "-H localhost", "-P 8080", "app:main"]
     