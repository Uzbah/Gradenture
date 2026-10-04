import logging
import sys

from loguru import logger

from backend.core.conf import settings
from backend.core.path_conf import LOG_DIR
from backend.utils.trace_id import get_trace_id

LOG_FORMAT = (
    '<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | '
    '<level>{level: <8}</level> | '
    '<cyan>{extra[trace_id]}</cyan> | '
    '<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>'
)


class InterceptHandler(logging.Handler):
    """Route stdlib logging (uvicorn, slowapi, httpx) through loguru.

    Without this, uvicorn's own handlers write in a different format and skip the
    trace id.
    """

    def emit(self, record: logging.LogRecord) -> None:
        try:
            level = logger.level(record.levelname).name
        except ValueError:
            level = record.levelno

        # Walk out of the logging machinery so the record points at the real caller.
        frame, depth = logging.currentframe(), 0
        while frame and (depth == 0 or frame.f_code.co_filename == logging.__file__):
            frame = frame.f_back
            depth += 1

        logger.opt(depth=depth, exception=record.exc_info).log(level, record.getMessage())


def _patch_trace_id(record: dict) -> None:
    record['extra']['trace_id'] = get_trace_id()


def setup_logging() -> None:
    """Configure loguru and hand the stdlib loggers over to it."""
    logger.remove()
    logger.configure(patcher=_patch_trace_id)
    logger.add(sys.stdout, level=settings.LOG_LEVEL, format=LOG_FORMAT, enqueue=True, backtrace=False)

    if settings.LOG_TO_FILE:
        LOG_DIR.mkdir(parents=True, exist_ok=True)
        logger.add(
            LOG_DIR / settings.LOG_FILE_NAME,
            level=settings.LOG_LEVEL,
            format=LOG_FORMAT,
            rotation='10 MB',
            retention='14 days',
            compression='zip',
            enqueue=True,
        )

    logging.basicConfig(handlers=[InterceptHandler()], level=0, force=True)
    for name in ('uvicorn', 'uvicorn.error', 'uvicorn.access', 'slowapi', 'httpx', 'httpcore'):
        stdlib_logger = logging.getLogger(name)
        stdlib_logger.handlers = [InterceptHandler()]
        stdlib_logger.propagate = False


log = logger
