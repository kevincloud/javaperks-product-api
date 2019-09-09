FROM ubuntu:18.04
  
LABEL Kevin Cochran "kcochran@hashicorp.com"

RUN echo 'libc6 libraries/restart-without-asking boolean true' | debconf-set-selections
ENV DEBIAN_FRONTEND noninteractive

RUN apt-get update && apt-get upgrade -y
RUN apt-get install -y python3 python3-pip
RUN mkdir /app

COPY ./requirements.txt /app/requirements.txt

WORKDIR /app

RUN pip3 install -r requirements.txt

COPY ./product-app.py /app

ENTRYPOINT [ "python3" ]

CMD [ "product-app.py" ]
