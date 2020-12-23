FROM python:3.8.3

RUN mkdir -p /app
RUN useradd -ms /bin/bash appuser
RUN chown -R appuser:appuser /app

RUN mkdir -p /opt/runtime/
ADD scripts/* /opt/runtime/
USER appuser

ENTRYPOINT ["/opt/runtime/entrypoint.sh"]
CMD ["make", "run-server"]
