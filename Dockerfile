ARG PYTHON_VERSION=3
FROM python:${PYTHON_VERSION}@sha256:dfd2829c77f0e9765a32bf3e9ba3191ae693d914fedd714c379bc3a5a36f2a1a 
#                                       ^ arm64/v8
RUN  apt update \
 && apt install -y python3-dev python3-pil i2c-tools \
 && pip3 install image adafruit-circuitpython-ssd1306 psutil \
 && pip3 install --upgrade --pre rpi.gpio

COPY RackPi ~/RackPi/

CMD ["~/RackPi/RackPI.py"]
ENTRYPOINT ["python3"]