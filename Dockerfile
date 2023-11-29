FROM python:3.11.6-slim-bookworm as curl-stage

# Install curl ; remove apt cache to reduce image size
RUN apt-get -y update && apt-get -y install curl  && rm -rf /var/lib/apt/lists/*


FROM curl-stage as poetry-requirements-stage

WORKDIR /tmp

ENV HOME /root
ENV PATH=${PATH}:$HOME/.local/bin

# Install poetry
RUN curl -sSL https://install.python-poetry.org | POETRY_VERSION=1.7.0 python3 -

# Export requirements.txt
COPY ./pyproject.toml ./poetry.lock* /tmp/
RUN poetry export -f requirements.txt --output requirements.txt --without-hashes --no-interaction --no-cache --only=main


FROM curl-stage

WORKDIR /code

ENV \
    # Prevent Python from buffering stdout and stderr and loosing some logs (equivalent to python -u option)
    PYTHONUNBUFFERED=1 \
    # Prevent Pip from timing out when installing heavy dependencies
    PIP_DEFAULT_TIMEOUT=600 \
    # Prevent Pip from creating a cache directory to reduce image size
    PIP_NO_CACHE_DIR=1

# Install dependencies with pip from exported requirements.txt
COPY --from=poetry-requirements-stage /tmp/requirements.txt /code/requirements.txt
RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt

# Copy API files
COPY src ./src

# Add and set a non-root user
RUN useradd appuser
USER appuser

# Healthcheck
HEALTHCHECK CMD curl --fail http://localhost:8501/_stcore/health

EXPOSE 8501

# Start Streamlit
ENTRYPOINT ["streamlit"]
CMD ["run", "src/streamlit_app/main.py", "--server.port=8501", "--server.address=0.0.0.0"]
