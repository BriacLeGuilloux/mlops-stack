FROM briacleguillou/python-base:latest

COPY python/worker/requirements.txt /app/worker/requirements.txt
RUN pip install --no-cache-dir -r /app/worker/requirements.txt

COPY python/worker/ /app/worker/

WORKDIR /app/worker
EXPOSE 8000
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
