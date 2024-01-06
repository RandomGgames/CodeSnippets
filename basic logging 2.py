import logging
import os
import sys
logger = logging.getLogger(__name__)

def main():
    logger.debug(f'This is a debug message')
    logger.info(f'This is a info message')
    logger.warning(f'This is a warning message')
    logger.critical(f'This is a critical message')
    logger.fatal(f'This is a fatal message')
    logger.error(f'This is a error message')

if __name__ == '__main__':
    if os.path.exists('latest.log'): open('latest.log', 'w').close() # Clear latest.log if it exists
    
    # File handler
    file_handler = logging.FileHandler('latest.log', encoding='utf-8')
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(logging.Formatter('%(asctime)s.%(msecs)03d %(levelname)s: %(message)s', datefmt='%Y-%m-%d %H:%M:%S'))
    logger.addHandler(file_handler)
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(logging.Formatter('%(asctime)s.%(msecs)03d %(levelname)s: %(message)s', datefmt='%Y-%m-%d %H:%M:%S'))
    logger.addHandler(console_handler)
    
    # Set the overall logging level to DEBUG
    logger.setLevel(logging.DEBUG)
    
    # Set logging level for module
    logging.getLogger('sys').setLevel(logging.CRITICAL)
    
    try:
        main()
    except Exception as e:
        logger.exception(f'The script could no longer continue due to {repr(e)}.')
        exit(1)