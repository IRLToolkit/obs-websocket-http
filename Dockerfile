From python:3
COPY main.py entrypoint.sh ./
RUN pip install simpleobsws aiohttp
ENTRYPOINT [ "sh", "./entrypoint.sh" ]
