FROM python:3-slim

ENV InsideDocker Yes

RUN  apt update \
 && apt install -y python3-dev python3-pil i2c-tools gcc \
 && pip3 install image adafruit-circuitpython-ssd1306 psutil \
 && pip3 install --upgrade --pre rpi.gpio

COPY RackPi /home/RackPi/

CMD ["/home/RackPi/RackPI.py"]
ENTRYPOINT ["python3"]
