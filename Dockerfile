FROM apache/airflow:2.4.3

ENV PYTHONASYNCIODEBUG 1
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

COPY requirements.txt /requirements.txt

RUN pip install --user --upgrade pip
RUN pip install 'apache-airflow[pandas]'
RUN pip install --no-cache-dir --user -r /requirements.txt