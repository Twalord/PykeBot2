FROM python:3.10

WORKDIR /app

COPY ./requirements.txt .

RUN pip3 install -r requirements.txt

COPY ./PykeBot2 ./PykeBot2

COPY ./main.py .

COPY DiscordToken .

COPY RiotToken .

COPY ToornamentToken .

RUN wget https://github.com/mozilla/geckodriver/releases/download/v0.30.0/geckodriver-v0.30.0-linux64.tar.gz

RUN tar -xzf geckodriver-v0.30.0-linux64.tar.gz

RUN rm geckodriver-v0.30.0-linux64.tar.gz

CMD ["python3", "main.py"]