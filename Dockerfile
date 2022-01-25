FROM python:latest
RUN apt-get update && apt-get install -y libcups2-dev
RUN pip install pycups flask requests
COPY ./app ./
CMD [ "python", "./main.py" ]
