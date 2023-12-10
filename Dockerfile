FROM python:3.10-alpine
WORKDIR /app
COPY . .
RUN apk update && \
    apk add --no-cache gcc && \
    pip install -r requirements.txt
CMD ["python", "./main.py"]