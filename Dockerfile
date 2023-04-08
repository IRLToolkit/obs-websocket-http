From python:3
COPY entrypoint.sh requirements.txt ./
RUN pip install -r requirements.txt
COPY main.py ./
ENTRYPOINT [ "sh", "./entrypoint.sh" ]
