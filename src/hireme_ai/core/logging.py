import logging


def configure_logging() -> None:
    logging.basicConfig(level=logging.INFO, format="%(message)s")
    try:
        import structlog
    except ModuleNotFoundError:
        return
    structlog.configure(
        processors=[
            structlog.processors.add_log_level,
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.JSONRenderer(),
        ]
    )
