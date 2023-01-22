FROM python:3-alpine

WORKDIR /bmw
COPY main.py Pipfile* /bmw/
RUN pip3 install --upgrade pipenv bimmer_connected &&\
  pipenv install --system

ENTRYPOINT ["python3", "main.py"]
