from datetime import datetime
import queue
import time
import logging
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from watchdog.events import (
    FileCreatedEvent,
    FileModifiedEvent,
    FileSystemEventHandler,
)
from watchdog.observers import Observer
from queue import Queue
import os
import tracemalloc


class CustomHandler(FileSystemEventHandler):
    def __init__(self, queue: Queue) -> None:
        self.queue = queue

    def on_modified(self, event: FileModifiedEvent):
        LOG.info(f"file is modified: {event.src_path}")
        if event.is_directory:
            return
        self.run(event.src_path)

    def run(self, path: str) -> None:
        with open(path) as f:
            body = f.read().strip("\r\n")

        self.queue.put(body)


def save_pid():
    with open("pid", "w") as f:
        f.write(str(os.getpid()))


def create_figure(output_path: str) -> None:
    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, num=1, clear=True)
    fig.savefig("plot.png", dpi=100)
    plt.close(fig)


def run(body: str) -> None:
    LOG.info(f"queue body: {body}")
    intput_path, output_path = body.split(",")
    create_figure(output_path)
    with open(intput_path) as f:
        input_body = f.read()
    with open(output_path, "w") as f:
        f.write(input_body)
    LOG.info(f"write to {output_path}")


LOG = logging.getLogger(__file__)
LOG.setLevel(logging.INFO)
fh = logging.FileHandler("log")
fh.setLevel(logging.INFO)
LOG.addHandler(fh)


if __name__ == "__main__":
    q = Queue(1)
    event_handler = CustomHandler(q)
    obs = Observer()
    obs.schedule(event_handler, "ipc")
    obs.start()

    LOG.info("start")
    try:
        save_pid()
        while True:
            LOG.info("wait queue")
            body = q.get()
            tracemalloc.start()
            run(body)
            LOG.info(tracemalloc.get_traced_memory())
            tracemalloc.stop()
    except:
        import traceback

        LOG.error(traceback.format_exc())
        obs.stop()
        obs.join()
