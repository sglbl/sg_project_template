FROM python:3.10.12-slim

RUN apt update && apt install ffmpeg -y

RUN pip install --upgrade pip

COPY requirements.txt . 

RUN pip3 install requirements.txt
# --no-cache-dir 

WORKDIR /app

COPY app ./app

COPY data/images ./data/images

COPY data/input ./data/input

RUN mkdir data/models

EXPOSE 8000

RUN python3 src/model_downloader.py
# # If you use local docker build, uncomment the following lines
# COPY models/gliner_model_weight.pt ./models/gliner_model_weight.pt
# COPY models/mdeberta-v3-base ./models/mdeberta-v3-base

CMD ["python3", "app/main.py"]

