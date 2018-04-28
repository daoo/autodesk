FROM alpine:edge

RUN apk update && apk --no-cache add python3
RUN python3 -m pip install --upgrade pip

COPY autodesk /autodesk/autodesk/
COPY config /autodesk/config/
COPY setup.cfg setup.py /autodesk/
WORKDIR /autodesk

RUN python3 -m pip install .

CMD ["python3", "-u", "-m", "autodesk.program", "/etc/autodesk.yml"]
