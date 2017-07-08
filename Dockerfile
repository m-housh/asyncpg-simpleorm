FROM mhoush/tox 

RUN apk add --update gcc musl-dev git && \
    pyenv global 3.6.1 && \
    pip install -r /usr/src/app/requirements_dev.txt && \
    pip install -e /usr/src/app && \
    rm -rf /var/tmp/* /var/cache/apk/* /tmp/* /root/.cache/*

CMD ["make", "run-tests"]
