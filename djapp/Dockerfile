# Dockerfile for Django Applications
# Ref: https://faun.pub/the-near-perfect-dockerfile-for-django-applications-8bc352a1e871

# Section1: Base Image
FROM python:3.8-slim
MAINTAINER YongHui

# Section2: Python Interpreter Flags
ENV PYTHONUNBUFFERED 1
ENV PYTHONDONTWRITEBYTECODE 1

# Section3: Compiler and OS libraries
ENV TZ Asia/Shanghai

RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime
RUN echo $TZ > /etc/timezone
RUN sed -i -e 's/deb.debian.org/mirrors.aliyun.com/g' /etc/apt/sources.list
RUN chmod 777 /tmp/ && apt update && apt install -y locales tzdata
RUN dpkg-reconfigure -f noninteractive tzdata
RUN localedef -i en_US -c -f UTF-8 -A /usr/share/locale/locale.alias en_US.UTF-8

ENV LANG en_US.UTF-8

RUN apt-get update \
  && apt-get install -y --no-install-recommends build-essential libpq-dev \
  && rm -rf /var/lib/apt/lists/*

# Section4: Project libraries and User Creation
COPY requirements.txt /tmp/requirements.txt

RUN pip3 install -U -i https://mirrors.aliyun.com/pypi/simple/ pip \
    && pip3 install -U -i https://mirrors.aliyun.com/pypi/simple/ -r /tmp/requirements.txt \
    && rm -rf /tmp/requirements.txt \
    && useradd -U app_user \
    && install -d -m 0755 -o app_user -g app_user /app/static

# Section5: Code and User Setup
WORKDIR /app

COPY . .
RUN chmod +x docker/*.sh

# Section6: Docker Run Checks and Configurations
ENTRYPOINT [ "docker/entrypoint.sh" ]

CMD [ "docker/start.sh" ]
