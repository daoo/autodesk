FROM alpine:latest

RUN apk --no-cache add python3

COPY autodesk /autodesk/autodesk/
COPY config /autodesk/config/
COPY setup.cfg setup.py /autodesk/
WORKDIR /autodesk

RUN pip3 install .

CMD ["python3", "-u", "-m", "autodesk.program", "/etc/autodesk.yml"]
