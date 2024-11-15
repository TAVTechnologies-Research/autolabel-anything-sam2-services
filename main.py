import os
import time
import atexit
import argparse

from core import BaseService
from logger import CustomLogger
from settings import settings
from services import Manager


# create a main function that can receive keyboard interrupts and call .stop() on the manager
def main(log_level: str, test: bool) -> None:
    logger = CustomLogger(level=log_level).get_logger()

    manager = Manager(settings, logger, test=test)
    manager.start()

    # try:
    #    while True:
    #        time.sleep(0.1)
    # except KeyboardInterrupt:
    #    manager.stop()
    #    logger.info("Manager stopped")
    #    return
    atexit.register(manager.stop)
    logger.success("Manager started")
    return


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--log-level",
        type=str,
        required=False,
        help="Log Level",
        default="TRACE",
    )
    parser.add_argument(
        "--test",
        type=int,
        required=False,
        help="Test mode for TaskManager (manual start needed if true)",
        default=1,
    )
    args = parser.parse_args()
    main(args.log_level, bool(args.test))
