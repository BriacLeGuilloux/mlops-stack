FROM python:3.11-slim

WORKDIR /app

RUN pip install --no-cache-dir \
    pandas==2.2.2 \
    numpy==1.26.4 \
    scikit-learn==1.5.0 \
    azure-storage-blob==12.20.0
