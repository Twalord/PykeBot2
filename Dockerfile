FROM python:3.11

WORKDIR /app

COPY ./requirements.txt .

RUN pip3 install -r requirements.txt

COPY ./PykeBot2 ./PykeBot2

COPY ./main.py .

COPY DiscordToken .

COPY RiotToken .

COPY ToornamentToken .

CMD ["python3", "main.py"]