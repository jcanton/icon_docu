from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import time

class NodeChangeHandler(FileSystemEventHandler):
    def __init__(self, on_change):
        self.on_change = on_change

    def on_modified(self, event):
        if event.src_path.endswith(".tex"):
            self.on_change()

def watch_node_files(directory, on_change):
    event_handler = NodeChangeHandler(on_change)
    observer = Observer()
    observer.schedule(event_handler, directory, recursive=True)
    observer.start()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()

