import os
import time
import threading
import signal

from typing import Any, Callable, Dict, List, Tuple

from settings import Settings, settings

ThreadTarget = Callable[..., Any]
ThreadInfo = List[Tuple[ThreadTarget, str, Tuple[Any, ...], Dict, threading.Thread]]


class BaseService:
    def __init__(self, src_settings: Settings, logger) -> None:
        self.log = logger
        self._settings = src_settings
        self.thread_info: ThreadInfo = []
        self.action_lock = threading.Lock()
        self.stop_event = threading.Event()
        self.__init_threads()

    def __init_threads(self) -> None:
        self.add_thread(target=self.thread_checker, name="ThreadChecker")

    def add_thread(self, target: ThreadTarget, name: str, *args, **kwargs) -> None:
        thread = threading.Thread(target=target, args=args, kwargs=kwargs)
        self.thread_info.append((target, name, args, kwargs, thread))

    def start(self):
        for target, name, args, kwargs, thread in self.thread_info:
            thread.start()
        self.log.info("All threads started")

    def stop(self):
        self.stop_event.set()
        with self.action_lock:
            self.log.critical("Stopping all threads")
            for target, name, args, kwargs, thread in self.thread_info:
                self.log.debug(f"Stopping {name} ---------------")
                thread.join()
                self.log.debug(f"{name} is stopped --------------q")
        self.log.info("All threads stopped")

    def check_thread_status(self) -> bool:
        is_alive = []
        for i, (target, name, args, kwargs, thread) in enumerate(self.thread_info):
            # if self.stop_state:
            if self.stop_event.is_set():
                return False
            if not thread.is_alive() and not self.stop_event.is_set():
                self.log.critical(f"Thread {name} is not alive")
                thread = threading.Thread(target=target, args=args, kwargs=kwargs)
                thread.start()
                self.log.critical(f"Thread {name} is restarted")
                self.thread_info[i] = (target, name, args, kwargs, thread)
            else:
                is_alive.append(True)

        return all(is_alive)

    def thread_checker(self):
        # while not self.stop_state:
        time.sleep(5)  # wait for the threads to start
        while not self.stop_event.is_set():
            # with self.action_lock:
            is_ok = self.check_thread_status()
            if self.stop_event.is_set():
                self.log.critical("THREADS CHECKED EVEN THOUGH THE STOP STATE IS TRUE")
            time.sleep(5)  # TODO: Parameterize checking interval
        self.log.critical("ThreadChecker is stopped due to stop_state is True")
