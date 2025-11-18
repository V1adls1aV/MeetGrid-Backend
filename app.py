import contextlib
import os
import subprocess
from collections.abc import Generator
from contextlib import contextmanager

from dotenv import load_dotenv
from testcontainers.redis import RedisContainer
from typer import Argument, Exit, Option, Typer

parser = Typer()


@parser.command()
def run(
    *,
    host: str = Option("localhost", help="Host to run the app on."),
    port: int = Option(8000, help="Port to run the app on."),
    ssl_certfile: str | None = Argument(None, help="SSL certificate file."),
    ssl_keyfile: str | None = Argument(None, help="SSL key file."),
    workers: int = Option(1, help="Number of CPU threads will be used to run the app."),
    init_env: bool = Option(False, help="Run redis container, like in tests."),
) -> None:
    """
    Run app in the production mode.
    """
    load_dotenv()
    command = [
        "uvicorn",
        "app.main:app",
        "--host",
        f"{host}",
        "--port",
        f"{port}",
        "--workers",
        f"{workers}",
    ]
    command.extend(["--ssl-certfile", ssl_certfile] if ssl_certfile else [])
    command.extend(["--ssl-keyfile", ssl_keyfile] if ssl_keyfile else [])

    with init_app_dependencies() if init_env else contextlib.nullcontext():
        process = subprocess.run(command)

    raise Exit(process.returncode)


@parser.command()
def test(
    *,
    test_path: str | None = Argument(None, help="Path to tests to execute."),
    verbose: bool = Option(False, help="Show log messages and tests output."),
    coverage: bool = Option(False, help="Show coverage report."),
    junit: bool = Option(False, help="Write JUnitXML output to 'junit.xml'."),
) -> None:
    """
    Run tests by a given path.
    """
    load_dotenv()
    command = ["pytest"] + ([test_path] if test_path else [])
    command.extend(
        [
            "--cov=app",
            "--cov-report",
            "term-missing:skip-covered",
            "--cov-report",
            "xml:coverage.xml",
        ]
        if coverage
        else []
    )
    command.extend(["-vvs", "--log-cli-level=DEBUG"] if verbose else ["-v"])
    command.extend(["--junit-xml=junit.xml"] if junit else [])
    with init_app_dependencies():
        process = subprocess.run(command)
    raise Exit(process.returncode)


@contextmanager
def init_app_dependencies() -> Generator[None, None, None]:
    with RedisContainer("redis:alpine") as redis:
        export_redis_container_credentials(redis)
        yield


def export_redis_container_credentials(redis: RedisContainer) -> None:
    redis_host = redis.get_container_host_ip()
    redis_port = redis.get_exposed_port(6379)

    os.environ["MEET_GRID__REDIS__HOST"] = redis_host
    os.environ["MEET_GRID__REDIS__PORT"] = str(redis_port)
    os.environ["MEET_GRID__REDIS__PASSWORD"] = redis.password if redis.password else ""
    os.environ["MEET_GRID__REDIS__DB"] = "0"


if __name__ == "__main__":
    OK = 0
    NO_TESTS_TO_RUN = 5
    parser()
