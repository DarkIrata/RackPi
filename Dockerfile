ARG PYTHON_VERSION=3
FROM python:${PYTHON_VERSION}

RUN  apt update \
 && apt install -y python3-dev python3-pil i2c-tools \
 && pip3 install image adafruit-circuitpython-ssd1306 psutil \
 && pip3 install --upgrade --pre rpi.gpio

COPY RackPi ~/RackPi/

CMD ["~/RackPi/RackPI.py"]
ENTRYPOINT ["python3"]