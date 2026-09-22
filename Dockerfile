FROM python:3.13

WORKDIR /app
COPY requirements.txt
COPY requirements-dev.txt
RUN pip install --no-cache-dir -r requirements-dev.txt

COPY . .
CMD["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "app:app" ]