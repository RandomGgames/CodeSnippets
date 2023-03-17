"""Copied from RMMUD and stripped slightly. Not working properly yet"""

def validateKeys(dictionary_to_check: dict, keys_to_check_exist: list = None, key_type_pairs: dict = None):
    """
    Validates that a given dictionary has a specific list of keys and optionally a value of certain type.
    
    Args:
        dictionary_to_check (dict): The dictionary to be checked for the keys.
        key_type_pairs (dict): A dictionary containing the keys to be checked and their corresponding types.
        dictionary_name (str): The name of the dictionary being checked for the log message.
    
    Returns:
        bool: True if all keys are present and have the expected types, False otherwise.
    """
    for key in key_type_pairs.keys():
        if not key in dictionary_to_check:
            raise KeyError("Number must be an integer.")
        if not isinstance(dictionary_to_check[key], key_type_pairs[key]):
            raise TypeError("Number must be an integer.")
    return True