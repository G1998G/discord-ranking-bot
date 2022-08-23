FROM python:3
RUN pip install --upgrade pip
RUN pip install --upgrade setuptools
RUN pip install discord
RUN mkdir bot
COPY main.py /bot
WORKDIR /bot
CMD ["python","main.py"]
