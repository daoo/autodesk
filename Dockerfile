FROM alpine:edge as builder
RUN apk update && apk --no-cache add python3
RUN python3 -m pip install --upgrade pip
COPY requirements.txt .
RUN python3 -m pip install -r requirements.txt
COPY . /autodesk
WORKDIR /autodesk
RUN python3 setup.py bdist_wheel
RUN pytest tests

FROM alpine:edge
RUN apk update && apk --no-cache add python3
RUN python3 -m pip install --upgrade pip
COPY --from=builder /autodesk/dist/*.whl /tmp/
RUN python3 -m pip install /tmp/*.whl
RUN rm /tmp/*.whl
CMD ["python3", "-u", "-m", "autodesk.program", "/etc/autodesk.cfg"]
