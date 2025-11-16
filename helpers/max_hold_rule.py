from decimal import Decimal
from typing import Optional, Tuple
import time


def evaluate_max_holding_rule(
    position_amt: Decimal,
    position_open_time: Optional[float],
    max_hold_minutes: int,
    now: Optional[float] = None,
) -> Tuple[Optional[float], bool]:
    """
    Evaluate the max holding time rule for the current position.

    Returns a tuple of (new_position_open_time, should_force_close).

    - If max_hold_minutes <= 0, the rule is disabled.
    - position_open_time is the timestamp (in seconds) when a non-zero position was first detected.
    """
    if now is None:
        now = time.time()

    # No open position -> reset timer and never trigger
    if position_amt <= 0:
        return None, False

    # Rule disabled: only maintain the open timestamp
    if max_hold_minutes <= 0:
        if position_open_time is None:
            position_open_time = now
        return position_open_time, False

    if position_open_time is None:
        position_open_time = now
        return position_open_time, False

    max_hold_seconds = max_hold_minutes * 60
    should_force_close = (now - position_open_time) >= max_hold_seconds
    return position_open_time, should_force_close


