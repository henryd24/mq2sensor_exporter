FROM python:3.10.7-alpine3.15

# Create user
RUN adduser -D mq2sensor

WORKDIR /app
COPY src/requirements.txt .

# Install required modules
RUN pip install --no-cache-dir -r requirements.txt && \
    rm -rf \
     /tmp/* \
     /app/requirements

COPY src/. .

USER mq2sensor

CMD ["python", "-u", "exporter.py"]

HEALTHCHECK --timeout=10s CMD wget --no-verbose --tries=1 --spider http://localhost:${GAS_PORT:=9595}/