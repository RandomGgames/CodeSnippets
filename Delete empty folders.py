from send2trash import send2trash

import datetime
import os
import pathlib
import socket
import sys
import time
import typing

import logging
logger = logging.getLogger(__name__)

"""
Delete empty folders.py

This script scans every folder in the directory it is run from and deletes any folders that contain 0 files from the bottom up.

Optionally, ignore_specifically and ignore_completely can be defined:
ignore_specifically: A path has to match these exact string(s) in order to be ignored.
ignore_completely: A path has to match any part of these string(s) in order to be ignored.
"""

log_location = 'delete empty folders.log'
ignore_specifically = [
    'R:\\OBS',
    'R:\\NVidia',
]
ignore_completely = [
    '$',
    'System',
]

def dir_is_empty(directory):
    for _, _, files in os.walk(directory):
        if files:
            return False
    return True

def main():
    start_time = time.perf_counter()
    
    logger.info('Deleting empty dirs...')
    
    deleted_dirs_count = 0
    deleted_dir_paths = []
    for root, dirs, _ in os.walk(os.path.dirname(os.path.realpath(__file__)), topdown=False):
        for dir_name in dirs:
            dir_path = os.path.join(root, dir_name)
            logger.debug(f'Scanning "{dir_path}"')
            if any(ignored in dir_path for ignored in ignore_completely):
                logger.debug(f'Part of dir is in "ignore_completely" list.')
                continue
            else:
                logger.debug(f'No part of dir is in "ignore_completely" list.')
            if dir_path in ignore_specifically:
                logger.debug(f'Dir is in "ignore_specifically" list.')
                continue
            else:
                logger.debug(f'Dir is not in "ignore_specifically" list.')
            logger.debug(f'Checking if dir is empty')
            if dir_is_empty(dir_path):
                logger.debug(f'Dir is empty')
                deleted_dir_paths.append(dir_path)
                send2trash(dir_path)
                deleted_dirs_count += 1
                logger.info(f'Deleted "{dir_path}"')
            else:
                logger.debug(f'Dir is not empty. Ignoring.')
    
    if deleted_dirs_count == 1:
        logger.info(f'Deleted {deleted_dirs_count} directories.')
    else:
        logger.info(f'Deleted {deleted_dirs_count} directories.')
    
    for dir_path_deleted in deleted_dir_paths:
        logger.info(f'Deleted directory "{dir_path_deleted}"')
    
    end_time = time.perf_counter()
    duration = end_time - start_time
    logger.debug(f'Completed operation in {duration:.4f}s.')

def setup_logging(
        logger: logging.Logger,
        log_file_path: typing.Union[str, os.fspath],
        number_of_logs_to_keep: typing.Union[int, None] = None,
        console_logging_level = logging.DEBUG,
        file_logging_level = logging.DEBUG,
        log_message_format = '%(asctime)s.%(msecs)03d [%(name)s] [%(funcName)s] %(levelname)s: %(message)s',
        date_format = '%Y-%m-%d %H:%M:%S'):
    # Initialize logs folder
    log_dir = os.path.dirname(log_file_path)
    if not os.path.exists(log_dir):
        os.makedirs(log_dir) # Create logs dir if it does not exist
    
    # Limit # of logs in logs folder
    if number_of_logs_to_keep is not None:
        log_files = sorted([f for f in os.listdir(log_dir) if f.endswith('.log')], key=lambda f: os.path.getmtime(os.path.join(log_dir, f)))
        if len(log_files) >= number_of_logs_to_keep:
            for file in log_files[:len(log_files) - number_of_logs_to_keep + 1]:
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
    #logging.getLogger('requests').setLevel(logging.INFO)
    #logging.getLogger('sys').setLevel(logging.CRITICAL)
    #logging.getLogger('urllib3').setLevel(logging.INFO)

if __name__ == '__main__':
    pc_name = socket.gethostname()
    script_name = pathlib.Path(os.path.basename(__file__)).stem
    log_dir = pathlib.Path(f'{script_name} Logs')
    timestamp = datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
    log_file_name = pathlib.Path(f'{timestamp}_{pc_name}.log')
    log_file_path = os.path.join(log_dir, log_file_name)
    setup_logging(logger, log_file_path, number_of_logs_to_keep=10)
    
    error = 0
    try:
        main()
    except Exception as e:
        logger.warning(f'A fatal error has occurred due to {repr(e)}')
        error = 1
    finally:
        exit(error)