import logging
from pathlib import Path
import os

def remove_old_log_files(logs_to_keep: int):
	"""
	Removes old log files in the 'logs' directory, keeping a specified number of logs.
	
	Args:
		logs_to_keep (int): The number of most recent log files to keep.
	"""

	logging.info('Deleting old log files.')
	try:
		logs_dir = Path('logs')
		if not logs_dir.exists():
			logging.exception(f'Logs directory "{logs_dir}" not found.')
			raise
		
		logging.debug('Getting list of log files to delete.')
		old_logs = list(sorted(logs_dir.iterdir(), key=os.path.getctime, reverse=False))[1:]
		old_logs.reverse()
		old_logs = old_logs[logs_to_keep:]
		logging.info(f'Found {len(old_logs)} log(s) to remove.')
		
		if len(old_logs) > 1:
			old_logs_deleted = 0
			for old_log in old_logs:
				try:
					os.remove(old_log)
					logging.info(f'Deleted "{old_log}".')
					old_logs_deleted += 1
				except FileNotFoundError:
					logging.warning(f'Cannot delete old log file "{old_log}". File not found.')
				except Exception as e:
					logging.warning(f'Cannot delete old log file "{old_log}". {repr(e)}')
			logging.info(f'Deleted {old_logs_deleted} old log(s).')
	
	except Exception as e:
		logging.warning(f'An error occurred while removing old log files: {repr(e)}')