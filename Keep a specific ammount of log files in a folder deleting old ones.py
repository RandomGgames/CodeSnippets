import logging
from pathlib import Path
import os

def removeOldLogFiles():
	"""Remove old logs based on limit in config"""
	logging.debug(f'Deleting old log files.')
	logs_to_keep = 30
		
	logging.debug(f'Getting list of log files to delete.')
	old_logs = list(sorted(Path('logs').iterdir(), key = os.path.getctime, reverse = False))[1:] #Source: https://stackoverflow.com/a/539024/16383324
	old_logs.reverse()
	old_logs = old_logs[logs_to_keep:]
	logging.debug(f'Found {len(old_logs)} log(s) to remove.')
	
	if len(old_logs) > 1:
		old_logs_deleted = 0
		for old_log in old_logs:
			try:
				os.remove(old_log)
				logging.debug(f'Deleted "{old_log}".')
				old_logs_deleted += 1
			except Exception as e:
				logging.warn(f'Cannot delete old log file "old_log". {repr(e)}')
		logging.debug(f'Deleted {old_logs_deleted} old log(s).')