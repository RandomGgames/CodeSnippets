"""
Functions for printing formatted text to the console
"""

import logging

logger = logging.getLogger(__name__)


class Styles:
    """Color and formatting styles"""
    # Text Effects
    RESET = "\033[0m"
    BOLD = "\033[1m"
    DIM = "\033[2m"
    ITALIC = "\x1B[3m"
    UNDERLINED = "\033[4m"
    BLINK = "\033[5m"
    REVERSE = "\033[7m"
    STRIKETHROUGH = "\033[9m"

    # Standard Colors
    BLACK = "\033[30m"
    RED = "\033[31m"
    GREEN = "\033[32m"
    YELLOW = "\033[33m"
    BLUE = "\033[34m"
    PURPLE = "\033[35m"
    CYAN = "\033[36m"
    WHITE = "\033[37m"

    # Bright Colors (Your original list mostly used these)
    GRAY = "\033[90m"
    BRIGHT_RED = "\033[91m"
    BRIGHT_GREEN = "\033[92m"
    BRIGHT_YELLOW = "\033[93m"
    BRIGHT_BLUE = "\033[94m"
    BRIGHT_PURPLE = "\033[95m"
    BRIGHT_CYAN = "\033[96m"
    BRIGHT_WHITE = "\033[97m"

    # Backgrounds
    BLACK_BG = "\033[40m"
    RED_BG = "\033[41m"
    GREEN_BG = "\033[42m"
    YELLOW_BG = "\033[43m"
    BLUE_BG = "\033[44m"
    PURPLE_BG = "\033[45m"
    CYAN_BG = "\033[46m"
    WHITE_BG = "\033[47m"

    @classmethod
    def preview_styles(cls):
        """Preview all available styles, skipping methods and internal attributes."""
        # Get all attributes that are strings and don't start with underscore
        style_names = [
            name for name in dir(cls)
            if not name.startswith("_") and isinstance(getattr(cls, name), str)
        ]

        for name in sorted(style_names):
            logger.debug(f"{name.ljust(15)}: {getattr(cls, name)}ABCabc#@!?0123{cls.RESET}")


class ColorFormatter(logging.Formatter):
    """Adds colors to specific keywords for console output only."""

    def format(self, record):
        message = super().format(record)
        if "PASS" in message:
            message = message.replace("PASS", f"{Styles.GREEN_BG}{Styles.BOLD}PASS{Styles.RESET}")
        elif "FAIL" in message:
            message = message.replace("FAIL", f"{Styles.RED_BG}{Styles.BOLD}FAIL{Styles.RESET}")

        return message

# Example usage:
# console_handler.setFormatter(ColorFormatter(message_format, datefmt=date_format))
