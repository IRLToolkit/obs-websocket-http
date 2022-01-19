From python:3
COPY src/main.py entrypoint.sh ./
RUN pip install -r src/requirements.txt
ENTRYPOINT [ "sh", "./entrypoint.sh" ]
