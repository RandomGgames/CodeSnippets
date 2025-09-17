import time


def countdown(timer: int, timer_message_prefix: str = '', timer_message_suffix: str = '') -> None:
    max_str_length = 0

    while timer > 0:
        if timer_message_prefix == '' and timer_message_suffix == '':
            message = str(timer)
        elif timer_message_prefix != '' and timer_message_suffix == '':
            message = f'{timer_message_prefix}{timer}'
        elif timer_message_prefix == '' and timer_message_suffix != '':
            message = f'{timer}{timer_message_suffix}'
        else:
            message = f'{timer_message_prefix}{timer}{timer_message_suffix}'
        max_str_length = max(len(message), max_str_length)
        while len(message) != max_str_length:
            message = f'{message} '  # Add spaces to end of line so previous entire line is replaced if new message is shorter
        print(message, end='\r')
        timer -= 1
        time.sleep(1)
    remove_message = ' ' * max_str_length
    print(remove_message, end='\r')
    return max_str_length


countdown(3)
print('Done!')

countdown(3, 'In ')
print('Done!')

countdown(3, 'In ', ' seconds')
print('Done!')
