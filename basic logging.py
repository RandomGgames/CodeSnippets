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
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s.%(msecs)03d %(levelname)s: %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S',
        encoding='utf-8',
        handlers=[
            logging.FileHandler('latest.log', encoding='utf-8'),
            logging.StreamHandler(sys.stdout)
        ]
    )
    
    # Set logging level for module
    logging.getLogger('sys').setLevel(logging.CRITICAL)
    
    try:
        main()
    except Exception as e:
        logger.exception(f'The script could no longer continue due to {repr(e)}.')
        exit(1)