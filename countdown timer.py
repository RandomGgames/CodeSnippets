import time

def countdown(timer: int) -> None:
    max_str_length = 0
    
    while timer > 0:
        message = f'Measuring value1 in {timer}'
        max_str_length = max(len(message), max_str_length)
        while len(message) != max_str_length:
            message = f'{message} ' # Add spaces to end of line so previous entire line is replaced if new message is shorter
        print(message, end='\r')
        timer -= 1
        time.sleep(1)