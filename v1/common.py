from datetime import datetime


def seconds_difference(t1: str, t2: str) -> int:
    # Parse times
    fmt = "%I:%M %p"
    today = datetime.today().date()
    dt1 = datetime.combine(today, datetime.strptime(t1, fmt).time())
    dt2 = datetime.combine(today, datetime.strptime(t2, fmt).time())
    # Calculate difference in seconds
    diff = (dt2 - dt1).total_seconds()
    return int(diff)

