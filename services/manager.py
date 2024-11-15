import sys
import time
import queue
import asyncio
import threading
import subprocess as sp

from typing import Optional, Union, Any, List, Dict

import enums
import schemas
from core import BaseService
from db import RedisClient


class Manager(BaseService):
    def __init__(self, src_settings, logger, test: bool = False) -> None:
        """Manager service class

        Args:
            src_settings (Settings): General settings
            logger (CustomLogger): Logger object to log messages
            test (bool, optional): If true, workers should be started manually for test. Defaults to False.
        """
        self.settings = src_settings
        self.test = test

        super().__init__(src_settings, logger)

        self.redis = RedisClient(config=self.settings)

        self.action_worker_map = {
            enums.Task.INIT_MODEL.value: queue.Queue(),
            enums.Task.TERMINATE_MODEL.value: queue.Queue(),
            enums.Task.RESET.value: queue.Queue(),
        }

        self.processes: Dict[str, sp.Popen] = dict()

        self.process_lock = threading.Lock()

        self.__init_additional_threads()

    def __init_additional_threads(self) -> None:
        self.add_thread(
            target=self.get_manager_messages_thread_fn, name="GetManagerMessages"
        )
        self.add_thread(target=self.process_starter_thread_fn, name="ProcessStarter")
        self.add_thread(target=self.stop_worker_thread_fn, name="StopWorker")

    def get_manager_messages(self) -> Optional[schemas.Intercom]:
        """Consumes a message from task-manager stream from redis

        Returns:
            Optional[schemas.Intercom]: If a message is received, returns the message, else None
        """
        # msg = self.redis.dequeue(self.settings.MANAGER_QUEUE_NAME, count=1)
        # update from dequeue to stream consume
        msg = self.redis.stream_consume(
            stream_name=self.settings.MANAGER_STREAM_NAME,
            group_name="main",
            consumer_name=self.__repr__(),
            count=1,
            block=10,
            strategy="unprocessed",
        )
        if msg is None or len(msg) == 0:
            return None
        try:
            payload: schemas.Intercom = schemas.Intercom.model_validate_json(
                msg[-1][-1]
            )
            return payload
        except Exception as e:
            self.log.error(f"Error parsing message: {e}")
            return None

    def get_manager_messages_thread_fn(self) -> None:
        """Thread function to consume messages from task-manager stream from redis"""
        while not self.stop_event.is_set():
            msg = self.get_manager_messages()
            if msg is not None:
                self.log.debug(f"Received message: {msg}")
                if msg.task_type in self.action_worker_map.keys():
                    self.action_worker_map[msg.task_type].put(msg)
                else:
                    self.log.error(f"Unknown task type: {msg.task_type}")
            else:
                pass
                #self.log.trace("No messages received")
            time.sleep(0.1)

    def process_starter(self, msg: schemas.Intercom) -> None:
        """Starts a new process for the model initialization.
        Expected message is a initialize_model message

        Args:
            msg (schemas.Intercom): Message retrieved from the task-manager stream
        """
        self.redis.set(f"task:{msg.uuid}:status", enums.TaskStatus.STARTING.value)
        try:
            with self.process_lock:
                self.log.debug("Starting model initialization process")
                if not self.test:
                    self.processes[msg.uuid] = sp.Popen(
                        [
                            f"{sys.executable}",
                            "./worker.py",
                            "--uuid",
                            msg.uuid,
                        ]
                    )
            # set the process (task) configuration to redis
            #   this is used by the worker to get the configuration
            self.redis.set(f"task:{msg.uuid}:config", msg.model_dump_json())
        except Exception as e:
            self.log.error(f"Error starting process: {e}")
            self.redis.set(f"task:{msg.uuid}:status", enums.TaskStatus.FAILED.value)

    def process_starter_thread_fn(self) -> None:
        """Thread function to start a new process for the model initialization. Reads from the INIT_MODEL queue."""
        while not self.stop_event.is_set():
            try:
                msg = self.action_worker_map[enums.Task.INIT_MODEL.value].get(
                    timeout=0.1
                )
                self.process_starter(msg)
            except queue.Empty:
                pass

    def stop_worker(self, uuid: str) -> None:
        """Stops a worker process given the task uuid

        Args:
            uuid (str): Task uuid

        Returns:
            None: Only logs the result and updates the task status in redis
        """
        try:
            if not self.test:
                self.processes[uuid].terminate()
                self.processes[uuid].wait()
                self.log.critical(
                    f"Worker {uuid} stopped! -> wait return code: {self.processes[uuid].returncode}"
                )
            self.redis.set(
                f"task:{uuid}:status", enums.TaskStatus.STOPPED.value, ttl=60
            )
            task_keys = self.redis.get_keys_with_pattern(f"task:{uuid}:*")
            for key in task_keys:
                self.redis.set_expiration(key=key, ttl=60)
        except Exception as e:
            self.log.error(f"Error stopping worker: {e}")

    def stop_worker_thread_fn(self) -> None:
        """Thread function to stop a worker process. Reads from the TERMINATE_MODEL (internal) queue."""
        while not self.stop_event.is_set():
            try:
                msg = self.action_worker_map[enums.Task.TERMINATE_MODEL.value].get(
                    timeout=0.1
                )
                self.log.info(f"Stopping worker: {msg.uuid}")
                self.stop_worker(msg.uuid)
            except queue.Empty:
                pass

    def test_stop_worker(self) -> None:
        time.sleep(10)
        while not self.stop_event.is_set():
            with self.process_lock:
                for k, v in self.processes.items():
                    if v.poll() is None:
                        self.stop_worker(k)
