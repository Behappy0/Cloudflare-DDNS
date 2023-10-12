FROM python:alpine

ENV HOST_NAME=
ENV DOMAIN_NAME=
ENV TOKEN=
ENV TYPE=
ENV ARGS=

RUN set -ex \
    && pip install --no-cache-dir https://github.com/Behappy0/Cloudflare-DDNS/archive/master.zip

CMD /usr/local/bin/cloudflare-ddns -n ${HOST_NAME} -d ${DOMAIN_NAME} -k ${TOKEN} -t ${TYPE} ${ARGS}
