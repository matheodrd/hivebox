# Hivebox

> [!NOTE]
> This is a practical learning project. I followed requirements and guidelines from the [Dynamic DevOps Roadmap](https://devopsroadmap.io/projects/hivebox).

## Development

You can build and run Hivebox inside a container using the included [Dockerfile](./Dockerfile).

### Build and run with Docker

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

| Method | Endpoint   | Description                                    |
| ------ | ---------- | ---------------------------------------------- |
| GET    | `/version` | Returns the current version of the Hivebox API |
