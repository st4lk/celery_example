FROM centos/systemd

# install python 3
RUN yum -y update && yum install -y python3 make

RUN mkdir -p /app
RUN useradd -ms /bin/bash appuser
RUN chown -R appuser:appuser /app

RUN mkdir -p /opt/runtime/
ADD scripts/* /opt/runtime/

COPY config/systemd.conf /etc/systemd/system/celery.service

CMD ["/usr/sbin/init"]
