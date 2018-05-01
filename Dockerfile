FROM alpine:latest

RUN apk --no-cache add python3

COPY autodesk /autodesk/autodesk/
COPY config /autodesk/config/
COPY setup.cfg setup.py /autodesk/
WORKDIR /autodesk

RUN pip3 install .

ENV AUTODESK_ADDRESS="0.0.0.0" \
    AUTODESK_CONFIG="/autodesk/config/testing.yml" \
    AUTODESK_DATABASE="/tmp/autodesk.db" \
    AUTODESK_PORT="80"

EXPOSE "80"

CMD ["python3", "-u", "-m", "autodesk.program"]
