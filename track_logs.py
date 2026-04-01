"""
Track Logs

A log crawler designed to monitor multiple directories  for specific file patterns.
It tracks file read positions and modification timestamps to ensure that only
new or modified content is processed across script restarts.

The script utilizes a JSON-based cache to store byte offsets and modification 
times. It handles complex edge cases such as log rotation, file truncation 
(shrinking), character swaps (same size, different content), and Windows-specific 
file permission locks.

How to use the script:
1. Configure the Settings dataclasses at tht top as necessary.
2. Run the script.
3. Within a 'while True' loop in the main function:
    - Iterate over 'get_updated_files(config.script.log_dirs, files_cache)'.
    - Nested within that, iterate over 'get_new_lines(log_file, files_cache)'.
    - Perform your logic (e.g., logging, parsing) on each yielded line.
    - Save the 'files_cache' back to the JSON file if 'update_cache' is True.
"""

import json
import logging
import logging.handlers
import os
import platform
import re
import socket
import sys
import tempfile
import time
import typing
from dataclasses import dataclass, field, fields, asdict
from datetime import datetime
from logging.handlers import TimedRotatingFileHandler
from pathlib import Path

logger = logging.getLogger(__name__)

__version__ = "0.0.0"  # Major.Minor.Patch

logger = logging.getLogger(__name__)
log_buffer = logging.handlers.MemoryHandler(
    capacity=0,
    flushLevel=logging.CRITICAL,
    target=None,
)
logger.addHandler(log_buffer)
logger.setLevel(logging.DEBUG)


@dataclass
class ScriptSettings:
    files_cache_path = Path(r"logs_cache.json")
    log_dirs = {
        r"Logs 2": r".*log$"
    }
    polling_interval = 1  # Second(s)


@dataclass
class LogSettings:
    mode: typing.Literal["per_run", "latest", "per_day", "single_file", "ConsoleOnly"] = "per_day"
    folder: Path = Path(r"logs")
    console_level: int = logging.DEBUG
    file_level: int = logging.DEBUG
    date_format: str = "%Y-%m-%d %H:%M:%S"
    message_format: str = "%(asctime)s.%(msecs)03d %(levelname)s [%(funcName)s] - %(message)s"
    max_files: int | None = 10
    open_log_after_run: bool = False


@dataclass
class InternalSettings:
    use_config_file: bool = False


@dataclass
class RuntimeSettings:
    pause_on_error: bool = True
    always_pause: bool = False


@dataclass
class Config:
    script: ScriptSettings = field(default_factory=ScriptSettings)
    logs: LogSettings = field(default_factory=LogSettings)
    runtime: RuntimeSettings = field(default_factory=RuntimeSettings)


def get_updated_files(target_dirs, cache):
    """
    Identifies files that have changed since the last successful cache update.
    """
    for directory, pattern in target_dirs.items():
        try:
            regex = re.compile(pattern, re.IGNORECASE)
            path_dir = Path(directory)
            if not path_dir.is_dir():
                continue

            for file_path in path_dir.iterdir():
                if file_path.is_file() and regex.search(file_path.name):
                    key = str(file_path.resolve())
                    stat = file_path.stat()

                    last_offset, last_mtime = cache.get(key, [0, 0])

                    # Detection logic for Appends, Swaps, and Shrinks
                    if stat.st_mtime > last_mtime or stat.st_size != last_offset:
                        yield file_path
        except (re.error, OSError):
            continue


def get_new_lines(file_path, cache):
    """
    Yields lines from the file. Updates cache only after successful reading
    to prevent synchronization errors during debugging or crashes.
    """
    key = str(file_path.resolve())
    try:
        stat = file_path.stat()
        current_size = stat.st_size
        current_mtime = stat.st_mtime
        last_offset, last_mtime = cache.get(key, [0, 0])

        # Determine if we need a full re-read
        should_re_read = (
            current_size < last_offset or
            (current_mtime > last_mtime and current_size == last_offset) or
            key not in cache
        )

        read_offset = 0 if should_re_read else last_offset
        new_lines = []
        final_offset = last_offset

        # 1. Read the file content into a temporary list
        # This keeps the 'with open' block as short as possible
        with open(file_path, 'r', encoding='utf-8', errors='replace') as f:
            f.seek(read_offset)
            for line in f:
                clean_line = line.strip()
                if clean_line:
                    new_lines.append(clean_line)

            # Capture the final position while the file is definitely open
            final_offset = f.tell()

        # 2. Yield the lines to main()
        yield from new_lines

        # 3. ONLY update the cache once all lines have been successfully yielded
        # This ensures main()'s 'update_cache' logic remains accurate.
        cache[key] = [final_offset, current_mtime]

    except (PermissionError, FileNotFoundError, OSError):
        # On error, we return without updating the cache, triggering a retry.
        pass


def main():
    config = Config()

    if config.script.files_cache_path.exists():
        try:
            files_cache = load_cache(config.script.files_cache_path)
            if not isinstance(files_cache, dict):
                raise TypeError("File cache should be structured as a dictionary")
        except Exception as e:
            logger.warning("Could not read %s: %s", json.dumps(str(config.script.files_cache_path.as_posix())), e)
            files_cache = {}
    else:
        files_cache = {}

    try:
        while True:
            update_cache = False
            for log_file in get_updated_files(config.script.log_dirs, files_cache):
                for line in get_new_lines(log_file, files_cache):
                    update_cache = True
                    """Line handling logic here"""
                    logger.debug("%s: %s", json.dumps(str(log_file.name)), line)

            if update_cache:
                save_cache(config.script.files_cache_path, files_cache)

            time.sleep(config.script.polling_interval)

    except KeyboardInterrupt:
        logger.debug("Process interrupted by user.")


def read_json_file(file_path: Path) -> dict | list | None:
    """
    Safely reads and parses a JSON file.
    """
    if not file_path.exists():
        logger.warning("File not found: %s", json.dumps(str(file_path)))
        raise FileNotFoundError("File not found")

    try:
        data = json.loads(file_path.read_text(encoding='utf-8'))
        logger.info("Successfully read data from %s", json.dumps(str(file_path)))
        return data

    except json.JSONDecodeError as e:
        logger.error("Invalid JSON format in %s: %s", json.dumps(str(file_path)), e)
        return None

    except Exception as e:
        logger.error("Unexpected error reading %s: %s", json.dumps(str(file_path)), e)
        return None


def write_json_file(file_path: Path, data: dict | list) -> bool:
    """
    Writes data to a JSON file atomically.
    """
    file_path = Path(file_path).absolute()

    if not file_path.parent.exists():
        file_path.parent.mkdir(parents=True, exist_ok=True)
        logger.debug("Created %s", json.dumps(str(file_path.parent.as_posix())))

    temp_file_path: Path | None = None
    try:
        with tempfile.NamedTemporaryFile(mode='w', dir=str(file_path.parent), encoding='utf-8', suffix=".tmp", delete=False) as tf:
            # Get file path from tempfile object
            temp_file_path = Path(tf.name)
            json.dump(data, tf, indent=4)
            tf.flush()
            os.fsync(tf.fileno())

        # Atomic swap
        temp_file_path.replace(file_path)
        logger.info("Successfully saved to %s", json.dumps(str(file_path)))
        return True

    except (KeyboardInterrupt, SystemExit):
        logger.error("Write interrupted for %s. Cleaning up.", json.dumps(str(file_path)))
        if temp_file_path and temp_file_path.exists():
            temp_file_path.unlink()
        raise

    except Exception as e:
        logger.error("Failed to write to %s: %s", json.dumps(str(file_path)), e)
        if temp_file_path and temp_file_path.exists():
            temp_file_path.unlink()
        return False


def load_config(file_path: Path) -> Config:
    config = Config()
    needs_sync = False

    try:
        external_config = read_json_file(file_path)
        if not isinstance(external_config, dict):
            external_config = {}
            needs_sync = True
    except FileNotFoundError:
        external_config = {}
        needs_sync = True
    except Exception:
        raise

    # Merge logic
    for section in fields(config):
        section_name = section.name
        if section_name not in external_config:
            needs_sync = True
            continue

        section_instance = getattr(config, section_name)
        json_values = external_config[section_name]

        for f in fields(section_instance):
            if f.name in json_values:
                val = json_values[f.name]
                if f.type is Path and isinstance(val, str):
                    val = Path(val)
                setattr(section_instance, f.name, val)
            else:
                needs_sync = True

    # Check for keys in external config that aren't in internal config
    internal_field_names = {f.name for f in fields(config)}
    if any(k for k in external_config if k not in internal_field_names):
        needs_sync = True

    if needs_sync:
        def path_serializer(obj):
            if isinstance(obj, Path):
                return str(obj)
            raise TypeError(f"Type {type(obj)} not serializable")

        # We re-serialize the internal_config (which now has merged data)
        # This naturally prunes extra keys because they weren't in the dataclass!
        synced_config = json.loads(json.dumps(asdict(config), default=path_serializer))
        write_json_file(file_path, synced_config)

    return config


def save_config(file_path: Path, config_data: dict | list) -> bool:
    """Alias for write_json_file, specifically for configuration files."""
    return write_json_file(file_path, config_data)


def load_cache(file_path: Path) -> dict | list | None:
    """Alias for read_json_file, specifically for cache files."""
    return read_json_file(file_path)


def save_cache(file_path: Path, cache_data: dict | list) -> bool:
    """Alias for write_json_file, specifically for cache files."""
    return write_json_file(file_path, cache_data)


def read_text_file(file_path: Path, as_list: bool = False) -> str | list[str] | None:
    """
    Reads a text file as a single string or a list of lines.

    Args:
        file_path: Path to the file.
        as_list: If True, returns a list of strings (lines). If False, one string.
    """
    if not file_path.exists():
        logger.warning("File not found: %s", file_path)
        return None

    try:
        if as_list:
            # .read_text().splitlines() is cleaner than .readlines()
            # as it handles different OS line endings automatically
            data = file_path.read_text(encoding='utf-8').splitlines()
        else:
            data = file_path.read_text(encoding='utf-8')

        logger.info("Successfully read text from %s", file_path)
        return data

    except Exception as e:
        logger.error("Unexpected error reading %s: %s", file_path, e)
        return None


def write_text_file(file_path: Path, data: str | list[str]) -> bool:
    """
    Writes a string or a list of strings to a text file atomically.
    """
    file_path = Path(file_path).absolute()

    if not file_path.parent.exists():
        file_path.parent.mkdir(parents=True, exist_ok=True)
        logger.debug("Created %s", json.dumps(str(file_path.parent.as_posix())))

    temp_file_path: Path | None = None
    try:
        with tempfile.NamedTemporaryFile(mode='w', dir=str(file_path.parent), encoding='utf-8', suffix=".tmp", delete=False) as tf:
            temp_file_path = Path(tf.name)

            if isinstance(data, list):
                # Add newlines if they aren't already there to ensure
                # list items don't all end up on one line
                tf.writelines(line if line.endswith('\n') else f"{line}\n" for line in data)
            else:
                tf.write(data)

            tf.flush()
            os.fsync(tf.fileno())

        temp_file_path.replace(file_path)
        logger.info("Successfully saved text to %s", file_path)
        return True

    except (KeyboardInterrupt, SystemExit):
        logger.error("Write interrupted for %s. Cleaning up.", file_path)
        if temp_file_path and temp_file_path.exists():
            temp_file_path.unlink()
        raise

    except Exception as e:
        logger.error("Failed to write text to %s: %s", file_path, e)
        if temp_file_path and temp_file_path.exists():
            temp_file_path.unlink()
        return False


def enforce_max_log_count(dir_path: Path, max_count: int, script_name: str) -> None:
    """
    Enforce a maximum number of log files for this script.
    Deletes the oldest logs based on filename ordering.

    Rules:
    - Only affects files ending with `.log`
    - Only affects logs that contain the script_name
    - Sorting is done by filename (lexicographically)
    """
    if max_count <= 0:
        return
    if not dir_path.exists():
        return
    log_files = [
        f for f in dir_path.glob("*.log")
        if script_name in f.name
    ]
    if len(log_files) <= max_count:
        return
    log_files.sort(key=lambda p: p.name)
    to_delete = log_files[:-max_count]
    for file in to_delete:
        try:
            file.unlink()
            logger.debug("Removed %s", json.dumps(file.absolute().as_posix()))
        except Exception:
            # Avoid raising during bootstrap
            pass


def setup_logging(logger_obj: logging.Logger, log_settings: LogSettings) -> Path | None:
    """Set up file and console logging with flexible modes and rotation."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    day_stamp = datetime.now().strftime("%Y%m%d")
    script_name = Path(__file__).stem
    pc_name = socket.gethostname()

    log_path: Path | None = None

    if log_settings.mode != "ConsoleOnly":
        log_dir = (log_settings.folder if isinstance(log_settings.folder, Path) else Path(log_settings.folder))
        log_dir = log_dir.expanduser().resolve()
        if not log_dir.exists():
            log_dir.mkdir(parents=True, exist_ok=True)
            logger.debug("Created log folder: %s", log_dir.as_posix())

        match log_settings.mode:
            case "per_run":
                log_path = log_dir / f"{timestamp}__{script_name}__{pc_name}.log"
            case "latest":
                log_path = log_dir / f"latest_{script_name}__{pc_name}.log"
            case "per_day":
                log_path = log_dir / f"{day_stamp}__{script_name}__{pc_name}.log"
            case "single_file":
                log_path = log_dir / f"{script_name}__{pc_name}.log"
            case _:
                log_path = log_dir / f"{timestamp}__{script_name}__{pc_name}.log"

    logger_obj.handlers.clear()
    logger_obj.setLevel(logging.DEBUG)

    # Formatter
    formatter = logging.Formatter(
        log_settings.message_format,
        datefmt=log_settings.date_format,
    )

    # File handler
    file_handler: logging.Handler | None = None
    if log_path:
        match log_settings.mode:
            case "per_day":
                file_handler = TimedRotatingFileHandler(
                    filename=log_path,
                    when="midnight",
                    interval=1,
                    backupCount=log_settings.max_files or 0,
                    encoding="utf-8",
                )
            case "single_file" | "latest" | "per_run":
                file_mode = "a" if log_settings.mode == "single_file" else "w"
                file_handler = logging.FileHandler(
                    log_path,
                    mode=file_mode,
                    encoding="utf-8",
                )
    if file_handler:
        file_handler.setLevel(log_settings.file_level)
        file_handler.setFormatter(formatter)
        logger_obj.addHandler(file_handler)

    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(log_settings.console_level)
    console_handler.setFormatter(formatter)
    logger_obj.addHandler(console_handler)

    # Flush logs buffer from prior to logging initialization
    if "log_buffer" in globals():
        class _ForwardToLogger(logging.Handler):
            def emit(self, record):
                logger_obj.handle(record)

        forward_handler = _ForwardToLogger()
        log_buffer.setTarget(forward_handler)
        log_buffer.flush()
        log_buffer.close()

    # Enforce max log count (except per_day which rotates automatically)
    if log_settings.max_files and log_path and log_settings.mode not in ("per_day", "ConsoleOnly"):
        try:
            enforce_max_log_count(
                dir_path=log_path.parent,
                max_count=log_settings.max_files,
                script_name=script_name,
            )
        except Exception as e:
            logger_obj.debug("Log pruning skipped: %s", e)

    return log_path


def bootstrap():
    exit_code = 0
    log_path = None
    script_path = Path(__file__)

    logger.info("=" * 80)

    config = Config()
    config_path = script_path.with_name(f"{script_path.stem}_config.json")
    global_settings = InternalSettings()
    if global_settings.use_config_file:
        config = load_config(config_path)

    try:
        log_path = setup_logging(logger_obj=logger, log_settings=config.logs)
        logger.info("%-10s %s", "Version:", __version__)
        logger.info("%-10s %s on %s", "User/Host:", os.getlogin(), socket.gethostname())
        logger.info("%-10s %s %s (v%s)", "Platform:", platform.system(), platform.release(), platform.version())
        logger.info("%-10s Python %s", "Runtime:", sys.version.split()[0])
        logger.info("%-10s %s", "Directory:", Path.cwd().as_posix())
        logger.info("%-10s %s", "AppConfig:", config)

        main()

    except KeyboardInterrupt:
        logger.warning("Operation interrupted by user.")
        exit_code = 130
    except Exception as e:
        logger.exception("A fatal error has occurred: %s", e)
        exit_code = 1
    finally:
        for handler in logger.handlers[:]:
            handler.close()
            logger.removeHandler(handler)

    if config.logs.open_log_after_run and log_path and log_path.exists():
        try:
            match sys.platform:
                case plat if plat.startswith("win"):  # Windows
                    os.startfile(log_path)
                case "darwin":  # macOS
                    os.system(f'open "{log_path}"')
                case _:  # Linux / others
                    os.system(f'xdg-open "{log_path}"')
        except Exception as e:
            logger.warning("Failed to open log file: %s", e)

    if config.runtime.always_pause or (config.runtime.pause_on_error and exit_code != 0):
        input("Press Enter to exit...")

    return exit_code


if __name__ == "__main__":
    sys.exit(bootstrap())
