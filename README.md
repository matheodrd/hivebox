# Hivebox

> [!NOTE]
> This is a practical learning project. I followed requirements and guidelines from the [Dynamic DevOps Roadmap](https://devopsroadmap.io/projects/hivebox).

## About

Hivebox is an API that provides environmental insights for beekeepers by aggregating data from community maintained sensors.

### Data source: OpenSenseMap

This project uses data from [OpenSenseMap](https://opensensemap.org), a citizen science platform for environmental data. OpenSenseMap is part of the [senseBox](https://sensebox.de) project, which enables people to build their own sensor stations and contribute environmental measurements (temperature, humidity, air quality, etc.) to a public database.

Thank you OpenSenseMap 😘

## Development

### Local development setup

#### Prerequisites

* Python 3.13+
* [uv](https://docs.astral.sh/uv/) package manager

#### Setup

1. Clone the repository and `cd` into it :

```sh
git clone git@github.com:matheodrd/hivebox.git
cd hivebox
```

2. Create a virtual environment using uv :

```sh
uv venv
```

3. Activate the virtual environement :

```sh
source .venv/bin/activate
```

4. Install dependencies with uv :

```sh
uv sync --group dev
```

This will install all project dependencies and development tools (FastAPI CLI, pytest, etc.).

#### Running tests

Run the unit tests :

```sh
pytest
```

Run tests with verbose output :

```sh
pytest -v
```

#### Running the API locally

Start the development server :

```sh
fastapi dev src/hivebox/main.py
```

The API will be available at `http://localhost:8000`.

### Build and run with Docker

You can also build and run Hivebox inside a container using the included [Dockerfile](./Dockerfile).

#### Build the image

```sh
docker build -t hivebox:latest .
```

This command creates a local image tagged hivebox:latest based on the Dockerfile in the project root.

The build process uses uv to install dependencies defined in pyproject.toml and uv.lock.

#### Run the container

```sh
docker run -p 8000:8000 hivebox:latest
```

This starts the API server on port 8000. You can access the API at `http://localhost:8000`.

#### API Documentation

Once the container is running, you can access the interactive API documentation at `http://localhost:8000/docs` (Swagger UI) or `http://localhost:8000/redoc` (Redoc).

### API Endpoints

| Method | Endpoint       | Description                                     |
| ------ | -------------- | ----------------------------------------------- |
| GET    | `/version`     | Returns the current version of the Hivebox API  |
| GET    | `/temperature` | Returns the average temperature from senseBoxes |
