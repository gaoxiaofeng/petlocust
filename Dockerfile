FROM locustio/locust

COPY requirements.txt /tmp/custom-requirements.txt

RUN pip3 install --upgrade -r /tmp/custom-requirements.txt