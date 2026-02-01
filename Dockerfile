FROM python:3.14.2

WORKDIR /app
COPY . .
RUN curl -sSL https://install.python-poetry.org | python3 - --version 2.3.1
RUN ~/.local/bin/poetry config virtualenvs.create false

RUN ~/.local/bin/poetry install

CMD [ "python", "-m", "src.main" ]
