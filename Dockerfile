FROM alpine:3.8 as builder

RUN apk --no-cache add python3-dev gcc musl-dev

RUN mkdir /install
WORKDIR /install

COPY requirements.txt /install/requirements.txt

RUN pip3 install --install-option="--prefix=/install" -r requirements.txt

FROM alpine:3.8

RUN apk --no-cache add python3

COPY --from=builder /install /usr/local
COPY autodesk /autodesk/autodesk/
COPY config /autodesk/config/
COPY setup.cfg setup.py /autodesk/
WORKDIR /autodesk

ENV AUTODESK_ADDRESS="0.0.0.0" \
    AUTODESK_CONFIG="/autodesk/config/testing.yml" \
    AUTODESK_DATABASE="/tmp/autodesk.db" \
    AUTODESK_PORT="80"

EXPOSE "80"

CMD ["python3", "-u", "-m", "autodesk.program"]
