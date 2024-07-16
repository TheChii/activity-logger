import os
import time
import logging
import psutil
import atexit

def setup_logger(name, log_file, level=logging.INFO):
    logs_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'logs'))
    os.makedirs(logs_dir, exist_ok=True)
    log_file_path = os.path.join(logs_dir, log_file)
    
    handler = logging.FileHandler(log_file_path)
    handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
    logger = logging.getLogger(name)
    logger.setLevel(level)
    logger.addHandler(handler)
    
    atexit.register(handler.close)
    
    return logger


process_logger = setup_logger('process', 'process.log')

def monitor_processes():
    process_logger.info("Started monitoring processes")
    try:
        while True:
            for process in psutil.process_iter(['pid', 'name', 'cmdline', 'ppid']):
                try:
                    process_info = f"Process found: {process.name()} (PID: {process.pid}) - Cmdline: {process.cmdline()} - Parent PID: {process.ppid()}"
                    process_logger.info(process_info)
                except psutil.NoSuchProcess as e:
                    process_logger.error(f"Process no longer exists: PID {process.pid}")
                except Exception as e:
                    process_logger.error(f"Error accessing process {process.pid}: {e}")
            time.sleep(1)
    except KeyboardInterrupt:
        process_logger.info("Stopped monitoring processes")
    except Exception as e:
        process_logger.error(f"Error in process monitoring: {e}")

if __name__ == "__main__":
    monitor_processes()
