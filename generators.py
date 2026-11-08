import logging
import secrets
import string

logger = logging.getLogger(__name__)


def generate_random_identifier(pattern: str = "*********", character_sets: dict[str, str] | None = None) -> str:
    """
    Generate a random identifier based on a customizable character pattern.

    The pattern determines which character set is used at each position.
    Characters not defined in character_sets are treated as literal characters.

    Args:
        pattern (str, optional): Defines the structure and format of the generated
            identifier. Each character in the pattern is evaluated individually:

            - If a character matches a key in character_sets, it is replaced
            with a randomly selected character from that character set.
            - If a character does not match a key, it is preserved literally
            in the generated identifier.

            Repeated pattern characters generate independent random selections.

            For example, with character_sets={"a": "ABC", "d": "3456"}:
                "aaaaa-ddddd" -> "ACBAB-54366"

            The hyphen is preserved because it is not a defined character set.
            Defaults to 12 uppercase letters (using the default "A" character set).
        character_sets (dict[str, str], optional): Mapping of pattern characters
            to their allowed character sets. Defaults to built-in character sets.

    Returns:
        str: Randomly generated identifier.

    Raises:
        TypeError: If pattern or character_sets have invalid types.
        ValueError: If pattern is empty or a character set is empty.
    """
    if not isinstance(pattern, str):
        raise TypeError(f"Pattern must be a string, got {type(pattern).__name__}")
    if not pattern:
        raise ValueError("Pattern cannot be empty")

    if character_sets is None:
        character_sets = {
            "U": string.ascii_uppercase,
            "L": string.ascii_lowercase,
            "#": string.digits,
            "*": string.ascii_uppercase + string.digits,
        }

    if not isinstance(character_sets, dict):
        raise TypeError(f"Character sets must be a dictionary, got {type(character_sets).__name__}")

    for key, characters in character_sets.items():
        if not isinstance(key, str) or len(key) != 1:
            raise ValueError(f"Character set keys must be single characters, got {key!r}")
        if not isinstance(characters, str):
            raise TypeError(f"Character set for {key!r} must be a string")
        if not characters:
            raise ValueError(f"Character set for {key!r} cannot be empty")

    identifier = ''.join(secrets.choice(character_sets[char]) if char in character_sets else char for char in pattern)

    return identifier


if __name__ == "__main__":
    while True:
        print(generate_random_identifier())
        input()
