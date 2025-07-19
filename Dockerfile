# Documentation on https://docs.astral.sh/uv/guides/integration/docker/

# Install python
FROM python:3.10

# Expose the port we wanna use
EXPOSE 8501
# As a UV project we need to download UV first
# Best pratice is to specified a uv version like uv:0.8.0
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Copy project into the image
ADD . /app

# Sync the project into a new env, asserting lockfile is up to date
WORKDIR /app
RUN uv sync --locked

# UV create a venv to install the dependencies, so we need to activate this venv and give the bin path
ENV VIRTUAL_ENV=/app/.venv
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

# Run the app
CMD ["streamlit", "run", "app.py"]