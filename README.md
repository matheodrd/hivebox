# Hivebox

> [!NOTE]
> This is a practical learning project. I followed requirements and guidelines from the [Dynamic DevOps Roadmap](https://devopsroadmap.io/projects/hivebox).

## Development

You can build and run Hivebox inside a container using the included [Dockerfile](./Dockerfile).

### Build and run with Docker

#### Build the image

```sh
docker build -t hivebox:0.0.1 .
```

This command creates a local image tagged hivebox:0.0.1 based on the Dockerfile in the project root.

The build process uses uv to install dependencies defined in pyproject.toml and uv.lock.

#### Run the container

```sh
docker run -p 8000:8000 hivebox:0.0.1
```

This currently just prints the version.
