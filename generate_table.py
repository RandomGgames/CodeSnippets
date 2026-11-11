from typing import Any
import logging

logger = logging.getLogger(__name__)


def _truncate_text(value: str, width: int) -> str:
    """
    Truncate text to fit within a specified width.

    Args:
        value: Text to truncate.
        width: Maximum number of characters allowed.

    Returns:
        The original text if it fits, otherwise truncated text ending with an ellipsis.

    Examples:
        >>> _truncate_text("Maintenance", 15)
        'Maintenance'
        >>> _truncate_text("Maintenance", 8)
        'Mainten…'
        >>> _truncate_text("Maintenance", 1)
        '…'
    """
    if len(value) <= width:
        return value

    if width == 1:
        return "…"

    return value[:width - 1] + "…"


def generate_table(rows: list[dict], columns: list[dict], padding: int = 1) -> str:
    """
    Generate a formatted table using the provided rows and column definitions.

    Column widths are calculated automatically based on their contents unless explicitly specified. Values exceeding their column width are truncated.

    Args:
        rows: A list of dictionaries containing the data to display. Each dictionary represents one table row.
        columns: A list of column definitions. Each definition must contain a "title" key and either a "key" or "getter" key. Optional keys include "width", "max_width", and "align". If "getter" is provided, it takes precedence over "key". The "max_width" option only applies when "width" is not specified. Alignment defaults to "left".
        padding: Number of spaces added to each side of a cell's contents. Defaults to 1.

    Returns:
        A formatted string containing the complete table.

    Raises:
        ValueError: If padding or column widths are invalid, or if a column has an unsupported alignment or non-callable getter.
        KeyError: If a column is missing its required definition keys.

    Examples:
        Print an empty table:
            print(generate_table([], [{"title": "ID", "key": "id"}]))

        Print a table with data:
            rows = [
                {"number": "1", "word": "apple", "description": "Crisp red fruit"},
                {"number": "2", "word": "banana", "description": "Tropical yellow fruit"},
                {"number": "3", "word": "carrot", "description": "Crunchy orange root"},
            ]
            columns = [
                {"title": "Numbers", "key": "number", "align": "center"},
                {"title": "Words", "key": "word", "width": 20},
                {"title": "Descriptions", "key": "description", "max_width": 15},
                {"title": "Uppercase", "getter": lambda row: row["word"].upper(), "align": "right"},
            ]
            print(generate_table(rows, columns, padding=2))
    """
    logger.debug("Generating table...")

    if not isinstance(padding, int) or isinstance(padding, bool) or padding < 0:
        raise ValueError("Padding must be a non-negative integer.")

    if not columns:
        return ""

    # Retrieve all row values before calculating column widths.
    column_values = []

    for column in columns:
        if "title" not in column:
            raise KeyError("Column definition is missing 'title'.")

        if "getter" in column:
            getter = column["getter"]

            if not callable(getter):
                raise ValueError(f"Column getter must be callable: {column['title']}")

            values = [str(getter(row)) for row in rows]

        elif "key" in column:
            values = [str(row.get(column["key"], "")) for row in rows]

        else:
            raise KeyError(f"Column '{column['title']}' is missing 'key' or 'getter'.")

        column_values.append(values)

    # Calculate column widths and validate column settings.
    widths = []

    for column, values in zip(columns, column_values):
        alignment = column.get("align", "left")

        if alignment not in ("left", "center", "right"):
            raise ValueError(f"Unsupported column alignment: {alignment!r}")

        width = column.get("width")

        if width is None:
            width = max(
                len(str(column["title"])),
                max((len(value) for value in values), default=0)
            )

            max_width = column.get("max_width")

            if max_width is not None:
                if not isinstance(max_width, int) or isinstance(max_width, bool) or max_width < 1:
                    raise ValueError("Maximum column width must be a positive integer.")

                width = min(width, max_width)

        elif not isinstance(width, int) or isinstance(width, bool) or width < 1:
            raise ValueError("Column width must be a positive integer.")

        widths.append(width)

    # Formatting helpers.
    def format_cell(value: Any, width: int, alignment: str = "left") -> str:
        value = _truncate_text(str(value), width)

        if alignment == "left":
            return f"{value:<{width}}"
        if alignment == "right":
            return f"{value:>{width}}"
        if alignment == "center":
            return f"{value:^{width}}"

        raise ValueError(f"Unsupported column alignment: {alignment!r}")

    def format_row(values: list[Any]) -> str:
        cells = [
            " " * padding
            + format_cell(value, width, column.get("align", "left"))
            + " " * padding
            for value, width, column in zip(values, widths, columns)
        ]

        return "│" + "│".join(cells) + "│"

    # Generate table borders.
    separator_segments = ["─" * (width + padding * 2) for width in widths]

    table = []

    table.append("┌" + "┬".join(separator_segments) + "┐")
    table.append(format_row([column["title"] for column in columns]))
    table.append("├" + "┼".join(separator_segments) + "┤")

    # Generate table contents.
    for values in zip(*column_values):
        table.append(format_row(list(values)))

    table.append("└" + "┴".join(separator_segments) + "┘")

    return "\n".join(table)
