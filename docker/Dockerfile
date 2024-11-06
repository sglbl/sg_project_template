FROM python:3.10.12-slim

RUN apt update && apt install ffmpeg -y

RUN pip install --upgrade pip

COPY requirements.txt . 

RUN pip3 install -r requirements.txt
# --no-cache-dir 

WORKDIR /app

COPY src ./app

COPY data/images ./data/images

RUN mkdir data/models

EXPOSE 8000

CMD ["python3", "-m", "src.main"]

