FROM python:3.10.12-slim

RUN apt update && apt install ffmpeg -y

RUN pip install --upgrade pip

COPY minreqs-cpu.txt . 

RUN pip3 install --use-deprecated=legacy-resolver -r minreqs-cpu.txt
# --no-cache-dir 

WORKDIR /app

RUN mkdir models

COPY app.py ./

COPY src ./src

COPY data/images ./data/images

COPY data/input ./data/input

EXPOSE 8000

RUN python3 src/model_downloader.py
# # If you use local docker build, uncomment the following lines
# COPY models/gliner_model_weight.pt ./models/gliner_model_weight.pt
# COPY models/mdeberta-v3-base ./models/mdeberta-v3-base

CMD ["python3", "app/main.py"]

