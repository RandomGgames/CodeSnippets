import os
from zipfile import ZipFile

def zipIsCorrupted(path):
    """
    Check if a zip file is corrupted by testing its integrity using ZipFile.testzip().
    
    Args:
        path (str): The path of the zip file to check.
    
    Returns:
        bool: True if the zip file is corrupted, False otherwise. If the file does not exist, return None.
    """
    if os.path.exists(path):
        with ZipFile(path) as zip_file:
            if zip_file.testzip() is not None:
                return True
            else:
                return False
    else:
        return None