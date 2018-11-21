FROM ubuntu:16.04
MAINTAINER yuan
ENV active prod

RUN apt-get update -y && apt-get upgrade -y && apt-get install python3-pip

RUN apt install tzdata

RUN echo "Asia/Shanghai" > /etc/timezone && dpkg-reconfigure -f noninteractive tzdata

RUN ln -snf /usr/share/zoneinfo/Asia/Shanghai /etc/localtime && echo "Asia/Shanghai" > /etc/timezone && dpkg-reconfigure -f noninteractive tzdata


RUN mkdir -p code

WORKDIR /code

COPY . /code


RUN pip3 install -i  https://pypi.doubanio.com/simple/  --trusted-host pypi.doubanio.com -r requirements.txt

RUN touch info.log

EXPOSE 5000

ENTRYPOINT python3 app.py >> info.log 2>&1 &