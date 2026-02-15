FROM python:3.13-bullseye

ENV LANG=C.UTF-8 \
  LC_ALL=C.UTF-8 

RUN rm -rf /var/lib/apt/lists/*
RUN apt-get update
RUN apt-get install -y --no-install-recommends build-essential

WORKDIR /github_dash
COPY . .

RUN pip install .

CMD mkdir -p /workspace
WORKDIR /workspace
