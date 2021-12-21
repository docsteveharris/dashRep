FROM python:3.9-buster
WORKDIR /app

ENV PYTHONFAULTHANDLER=1 \
  PYTHONUNBUFFERED=1 \
  PYTHONHASHSEED=random \
  PIP_NO_CACHE_DIR=off \
  PIP_DISABLE_PIP_VERSION_CHECK=on \
  PIP_DEFAULT_TIMEOUT=100 \
  POETRY_VERSION=1.1.1

# Install poetry and dependencies *before* the app
RUN python -m pip install "poetry==$POETRY_VERSION"
COPY poetry.lock pyproject.toml /app/
RUN poetry config virtualenvs.create false
# Does not install development tools
RUN poetry install --no-dev --no-interaction --no-ansi

COPY . /app
CMD ["python", "-u", "./app/hello.py"]