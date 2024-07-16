import time
import os
import logging
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

def setup_logger(name, log_file, level=logging.INFO):
    logs_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'logs'))
    os.makedirs(logs_dir, exist_ok=True)
    log_file_path = os.path.join(logs_dir, log_file)
    
    handler = logging.FileHandler(log_file_path)
    handler.setFormatter(logging.Formatter('%(asctime)s - %(message)s'))
    logger = logging.getLogger(name)
    logger.setLevel(level)
    logger.addHandler(handler)
    return logger

file_creation_logger = setup_logger('file_creation', 'file_creation.log')
file_deletion_logger = setup_logger('file_deletion', 'file_deletion.log')
file_modification_logger = setup_logger('file_modification', 'file_modification.log')


class MyHandler(FileSystemEventHandler):
    def on_created(self, event):
        file_creation_logger.info(f"File created: {event.src_path}")
    
    def on_deleted(self, event):
        file_deletion_logger.info(f"File deleted: {event.src_path}")
    
    def on_modified(self, event):
        if event.src_path.endswith('.log'):
            return
        
        file_modification_logger.info(f"File modified: {event.src_path}")


def monitor_directory(path):
    event_handler = MyHandler()
    observer = Observer()
    observer.schedule(event_handler, path, recursive=True)
    observer.start()
    file_creation_logger.info(f"Started monitoring {path}")
    file_deletion_logger.info(f"Started monitoring {path}")
    file_modification_logger.info(f"Started monitoring {path}")
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    except Exception as e:
        file_creation_logger.error(f"Error: {e}")
        file_deletion_logger.error(f"Error: {e}")
        file_modification_logger.error(f"Error: {e}")
    finally:
        observer.join()
        file_creation_logger.info(f"Stopped monitoring {path}")
        file_deletion_logger.info(f"Stopped monitoring {path}")
        file_modification_logger.info(f"Stopped monitoring {path}")

if __name__ == "__main__":
    path = "C:\\" if os.name == 'nt' else "/"
    monitor_directory(path)
