FROM ubautograding/python3.8-oracle-instantclient:latest

WORKDIR /app/backend
ENV PYTHONPATH=/app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

RUN mkdir -p mount

CMD python3 -u initialize_autolab.py && gunicorn --bind 0.0.0.0:5057 server:gunicorn_app
