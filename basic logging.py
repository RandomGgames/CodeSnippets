import logging
import os
import sys
logger = logging.getLogger()

def main():
    logger.debug(f'This is a debug message')
    logger.info(f'This is a info message')
    logger.warning(f'This is a warning message')
    logger.critical(f'This is a critical message')
    logger.fatal(f'This is a fatal message')
    logger.error(f'This is a error message')

if __name__ == '__main__':
    log_file = f'{os.path.basename(__file__).split(".")[0]}.log'
    clear_latest_log = True
    #Clear log file
    if clear_latest_log:
        if os.path.exists(log_file):
            open(log_file, 'w').close()
    #Setup logging
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s.%(msecs)03d %(levelname)s: %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S',
        encoding='utf-8',
        handlers=[
            logging.FileHandler(log_file, encoding='utf-8'),
            logging.StreamHandler(sys.stdout)
        ]
    )
    #Set specific logging levels
    pass
    logging.getLogger('sys').setLevel(logging.CRITICAL)
    
    try:
        main()
        error = 0
    except Exception as e:
        logger.warning(f'A fatal error has occured due to {repr(e)}')
        error = 1
    finally:
        exit(error)