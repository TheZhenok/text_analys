FROM python:3.10

# Set user and environment arguments
ARG USERNAME=app
ARG USER_UID=1000
ARG USER_GID=$USER_UID
ARG HOME=/usr/src/backend/
ARG ENVIRONMENT=development

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    ENVIRONMENT=${ENVIRONMENT} \
    POETRY_HOME=/etc/poetry \
    SHELL=/bin/bash

WORKDIR $HOME

COPY pyproject.toml poetry.lock* $HOME/

RUN addgroup --system $USERNAME && adduser --system --group $USERNAME && mkdir -p $HOME \
    && mkdir -p /etc/sudoers.d \
    && echo $USERNAME ALL=\(root\) NOPASSWD:ALL > /etc/sudoers.d/$USERNAME \
    && chmod 0440 /etc/sudoers.d/$USERNAME \
    && apt-get update \
    && apt-get install -y sudo curl git \
    && curl -sSL https://install.python-poetry.org | python3 - --git https://github.com/python-poetry/poetry.git@master \
    && cd /usr/local/bin && ln -s /etc/poetry/bin/poetry \
    && poetry config virtualenvs.create false \
    && apt-get clean && rm -rf /var/lib/apt/lists/*


COPY . /usr/src/backend/

# RUN chown -R $USERNAME:$USERNAME $HOME && \
#     if [ "$ENVIRONMENT" = "development" ]; then \
#         poetry install --no-root; \
#     else \
#         poetry install --no-root --only main; \
#     fi

USER root

EXPOSE 8049