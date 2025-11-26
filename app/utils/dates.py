from datetime import datetime


def normalize_datetime(date_string: str):
    """
    Convert various datetime formats to %Y-%m-%dT%H:%M:%S
    Handles both ISO format with timezone and without microseconds
    """
    if "." in date_string:
        date_string = date_string.split(".")[0]

    if "+" in date_string or date_string.count("-") > 2:
        for tz_char in ["+", "-"]:
            if tz_char in date_string[-6]:
                date_string = date_string.rsplit(tz_char, 1)[0]
                break

    return datetime.strptime(date_string, "%Y-%m-%dT%H:%M:%S")
