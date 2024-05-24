
FROM apache/superset:latest

USER root

RUN pip install mysqlclient

ENV SUPERSET_USERNAME $SUPERSET_USERNAME
ENV SUPERSET_EMAIL $SUPERSET_EMAIL
ENV SUPERSET_PASSWORD $SUPERSET_PASSWORD

COPY ./superset-init.sh /superset-init.sh
RUN chmod +x /superset-init.sh

EXPOSE 8088

ENTRYPOINT [ "/superset-init.sh" ]