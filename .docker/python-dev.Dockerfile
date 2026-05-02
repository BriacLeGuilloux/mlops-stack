FROM briacleguillou/python-base:latest

USER root

COPY python/trainer/requirements.txt /tmp/trainer-req.txt
COPY python/worker/requirements.txt /tmp/worker-req.txt
COPY tests/requirements.txt /tmp/test-req.txt

RUN pip install --no-cache-dir \
    -r /tmp/trainer-req.txt \
    -r /tmp/worker-req.txt \
    -r /tmp/test-req.txt

WORKDIR /workspace
RUN chown appuser:appuser /workspace

USER appuser
