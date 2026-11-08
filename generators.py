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
                pattern "aaaaa-ddddd" could generate "ACBAB-54366"

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


def generate_unique_random_identifier(existing_identifiers: list, pattern: str = "*********", character_sets: dict[str, str] | None = None, max_retries: int | None = 100) -> str:
    """
    Generate a random identifier that is guaranteed to be unique within a
    provided collection of existing identifiers.

    This function repeatedly generates identifiers using
    generate_random_identifier() until one is produced that does not already
    exist in existing_identifiers, or until the maximum number of attempts
    is reached.

    Args:
        existing_identifiers (list): Collection of identifiers that must not
            be duplicated. Membership is checked using the ``in`` operator.

        pattern (str, optional): Defines the structure and format of the
            generated identifier. Passed directly to
            generate_random_identifier(). Defaults to 12 uppercase letters
            and digits (using the default "*" character set).
            For example, with character_sets={"a": "ABC", "d": "3456"}:
                pattern "aaaaa-ddddd" could generate "ACBAB-54366"

        character_sets (dict[str, str], optional): Mapping of pattern
            characters to their allowed character sets. Passed directly to
            generate_random_identifier(). Defaults to built-in character sets.

        max_retries (int, optional): Maximum number of attempts to generate
            a unique identifier before giving up. Defaults to 100.

    Returns:
        str: A randomly generated identifier that does not exist in
        existing_identifiers.

    Raises:
        TypeError: Propagated from generate_random_identifier() if pattern
            or character_sets have invalid types.
        ValueError: Propagated from generate_random_identifier() if pattern
            is empty, a character set is empty, or max_retries is less than 1.
        RuntimeError: If a unique identifier cannot be generated within
            max_retries attempts.
    """
    if max_retries is not None:
        if not isinstance(max_retries, int):
            raise TypeError(f"Max retries must be an integer or None, got {type(max_retries).__name__}")
        if max_retries < 1:
            raise ValueError("Max retries must be greater than 0")

    logger.debug("Generating unique random identifier...")

    attempt = 0

    while True:
        attempt += 1

        generated_identifier = generate_random_identifier(pattern, character_sets)

        if generated_identifier not in existing_identifiers:
            return generated_identifier

        if max_retries is None:
            logger.debug('Generated a duplicate ID "%s" on attempt %d', generated_identifier, attempt,)
        else:
            logger.debug('Generated a duplicate ID "%s" on attempt %d/%d', generated_identifier, attempt, max_retries,)

            if attempt >= max_retries:
                raise RuntimeError(f"Failed to generate a unique identifier after {max_retries} attempts")
