import sys

from loguru import logger


class CustomLogger:
    def __init__(
        self,
        level="DEBUG",
        file_path="logs/app.log",
        rotation="10 MB",
        retention="30 days",
    ):
        # Configure the logger
        log_format_file = (
            "<green>{time:YYYY-MM-DD HH:mm:ss}</green>|<level>{level}</level>|"
            "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan>|<level>{message}</level>"
        )

        log_format = (
            "<level>{time:YYYY-MM-DD HH:mm:ss}</level> | <level>{level: <8}</level> | "
            "<level>{name:<15}</level> : <level>{function:<25}</level>:<cyan>{line:<4}</cyan>"
            ":<level>{thread:<10}</level> -"
            " <level>{message}</level>"
        )

        # Remove any previously added handlers, in case this is a reconfiguration
        logger.remove()
        # add fatal level red with white background

        # logger.level("INFO", color="<green>")
        # Add a new handler with the desired level and format
        # logger.add(sys.stderr, format=log_format, level=5, colorize=True, backtrace=True, enqueue=True)
        logger.add(
            sys.stderr,
            format=log_format,
            level=5,
            colorize=True,
            backtrace=True,
            enqueue=True,
        )

        # Add a file handler for logging to a file, with rotation and retention policies
        logger.add(
            file_path,
            format=log_format_file,
            level=level,
            rotation=rotation,
            retention=retention,
            enqueue=True,
        )

        # Keep a reference to the logger for use in your project
        self.logger = logger

    def get_logger(self):
        return self.logger


if __name__ == "__main__":
    log = CustomLogger(level="DEBUG").logger

    @log.catch
    def fail():
        raise Exception("This is a failure")

    log.debug("This is a debug message")
    fail()
