import os
import time
import logging
import winreg
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
registry_logger = setup_logger('registry', 'registry.log')

REG_NOTIFY_CHANGE_NAME = 0x00000001
REG_NOTIFY_CHANGE_LAST_SET = 0x00000004

def monitor_registry(key, sub_key):
    registry_logger.info(f"Started monitoring registry key: {key}\\{sub_key}")
    reg_key = winreg.OpenKey(key, sub_key, 0, winreg.KEY_NOTIFY | winreg.KEY_READ)
    
    try:
        while True:
            try:
                result = win32api.RegNotifyChangeKeyValue(
                    reg_key,
                    True,
                    REG_NOTIFY_CHANGE_NAME | REG_NOTIFY_CHANGE_LAST_SET,
                    None,
                    False
                )
                if result == 0:
                    registry_logger.info(f"Registry key changed: {key}\\{sub_key}")
                else:
                    registry_logger.warning(f"Unexpected result from registry change notification: {result}")
            except Exception as e:
                registry_logger.error(f"Error monitoring registry key: {e}")
            
            if os.getenv('RUNNING_UNDER_IDE', '0') == '1':
                break
            time.sleep(1)
    except KeyboardInterrupt:
        registry_logger.info("Stopped monitoring registry")
    except Exception as e:
        registry_logger.error(f"Error in registry monitoring loop: {e}")
    finally:
        winreg.CloseKey(reg_key)

if __name__ == "__main__":
    monitor_registry(winreg.HKEY_LOCAL_MACHINE, "SOFTWARE")
