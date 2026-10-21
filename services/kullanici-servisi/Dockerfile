FROM python:3.12-slim

WORKDIR /uygulama
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
COPY app ./app

EXPOSE 8001
CMD ["uvicorn", "app.main:uygulama", "--host", "0.0.0.0", "--port", "8001"]
