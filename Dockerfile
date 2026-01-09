FROM python:3.13.11

WORKDIR app
COPY . .
RUN curl -sSL https://install.python-poetry.org | python3 - --version 1.8.4
RUN ~/.local/bin/poetry config virtualenvs.create false

RUN ~/.local/bin/poetry install

CMD [ "python", "-m", "src.main" ]
