FROM python:3.6-slim

COPY . /root

WORKDIR /root

RUN pip install flask gunicorn markupsafe statistics numpy sklearn scipy joblib flask_wtf wtforms os werkzeug pandas