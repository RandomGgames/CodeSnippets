import logging
import os
from pathlib import Path
logger = logging.getLogger(__name__)

def remove_old_log_files(logs_to_keep: int):
    """
    Removes old log files in the 'logs' directory, keeping a specified number of logs.
    
    Args:
        logs_to_keep (int): The number of most recent log files to keep.
    """
    
    logger.info('Deleting old log files...')
    try:
        logs_dir = Path('logs')
        if not logs_dir.exists():
            logger.exception(f'Logs directory "{logs_dir}" not found.')
            raise
        
        logger.debug('Getting list of log files to delete...')
        old_logs = list(sorted(logs_dir.iterdir(), key=os.path.getctime, reverse=False))[1:]
        old_logs.reverse()
        old_logs = old_logs[logs_to_keep:]
        logger.info(f'Found {len(old_logs)} log(s) to delete.')
        
        if len(old_logs) > 1:
            old_logs_deleted = 0
            for old_log in old_logs:
                try:
                    os.remove(old_log)
                    logger.info(f'Deleted "{old_log}".')
                    old_logs_deleted += 1
                except FileNotFoundError:
                    logger.warning(f'Cannot delete old log file "{old_log}". File not found.')
                except Exception as e:
                    logger.warning(f'Cannot delete old log file "{old_log}". {repr(e)}')
            logger.info(f'Deleted {old_logs_deleted} old log(s).')
    
    except Exception as e:
        logger.warning(f'An error occurred while removing old log files: {repr(e)}')