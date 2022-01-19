From python:3
COPY main.py entrypoint.sh ./
RUN pip install -r requirements.txt
ENTRYPOINT [ "sh", "./entrypoint.sh" ]
