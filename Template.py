import datetime
import logging
import os
import sys
import typing
logger = logging.getLogger(__name__)

"""
Template.py

Description/explination here
"""

def main():
    pass

def setup_logging(
        logger: logging.Logger,
        log_file_path: typing.Union[str, os.fspath],
        max_log_files_to_keep: typing.Union[int, None] = None,
        console_logging_level = logging.DEBUG,
        file_logging_level = logging.DEBUG,
        log_message_format = '%(asctime)s.%(msecs)03d %(levelname)s: %(message)s',
        date_format = '%Y-%m-%d %H:%M:%S'):
    # Initialize logs folder
    log_dir = os.path.dirname(log_file_path)
    if not os.path.exists(log_dir):
        os.makedirs(log_dir) # Create logs dir if it does not exist
    
    # Limit # of logs in logs folder
    if max_log_files_to_keep is not None:
        log_files = sorted([f for f in os.listdir(log_dir) if f.endswith('.log')], key=lambda f: os.path.getmtime(os.path.join(log_dir, f)))
        if len(log_files) >= max_log_files_to_keep:
            for file in log_files[:len(log_files) - max_log_files_to_keep + 1]:
                os.remove(os.path.join(log_dir, file))
    
    logger.setLevel(file_logging_level)  # Set the overall logging level
    
    # File Handler for date-based log file
    file_handler_date = logging.FileHandler(log_file_path, encoding='utf-8')
    file_handler_date.setLevel(file_logging_level)
    file_handler_date.setFormatter(logging.Formatter(log_message_format))
    logger.addHandler(file_handler_date)
    
    # Console Handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(console_logging_level)
    console_handler.setFormatter(logging.Formatter(log_message_format, datefmt=date_format))
    logger.addHandler(console_handler)
    
    # Set specific logging levels
    #logging.getLogger('can').setLevel(logging.CRITICAL)
    #logging.getLogger('canopen').setLevel(logging.CRITICAL)
    #logging.getLogger('pcan').setLevel(logging.CRITICAL)
    #logging.getLogger('pyvisa').setLevel(logging.CRITICAL)
    #logging.getLogger('requests_negotiate_sspi').setLevel(logging.INFO)
    #logging.getLogger('sys').setLevel(logging.CRITICAL)
    #logging.getLogger('urllib3').setLevel(logging.INFO)

if __name__ == "__main__":
    # Set up logging
    script_name = os.path.splitext(os.path.basename(__file__))[0]
    log_dir = f"{script_name} Logs"
    log_file_name = f'{datetime.datetime.now().strftime('%Y-%m-%d %H-%M-%S')}.log'
    log_file_path = os.path.join(log_dir, log_file_name)
    setup_logging(logger, log_file_path)
    
    error = 0
    try:
        main()
    except Exception as e:
        logger.warning(f'A fatal error has occurred due to {repr(e)}')
        error = 1
    finally:
        exit(error)