FROM briacleguillou/python-base:latest

USER root

COPY python/trainer/requirements.txt /app/trainer/requirements.txt
RUN pip install --no-cache-dir -r /app/trainer/requirements.txt

COPY python/trainer/ /app/trainer/
RUN chown -R appuser:appuser /app/trainer

USER appuser
WORKDIR /app/trainer
CMD ["python", "train.py"]
