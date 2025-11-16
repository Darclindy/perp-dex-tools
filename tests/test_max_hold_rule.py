from decimal import Decimal

from helpers.max_hold_rule import evaluate_max_holding_rule


def test_no_position_resets_timer_and_never_triggers():
    open_time, should_close = evaluate_max_holding_rule(
        position_amt=Decimal("0"),
        position_open_time=123.0,
        max_hold_minutes=10,
        now=133.0,
    )
    assert open_time is None
    assert not should_close


def test_rule_disabled_only_tracks_open_time():
    # When disabled, it should only maintain the timestamp and never trigger close
    open_time, should_close = evaluate_max_holding_rule(
        position_amt=Decimal("1"),
        position_open_time=None,
        max_hold_minutes=0,
        now=1000.0,
    )
    assert open_time == 1000.0
    assert not should_close


def test_position_younger_than_threshold_does_not_trigger():
    open_time = 1000.0
    now = 1000.0 + 9 * 60  # 9 minutes later
    new_open_time, should_close = evaluate_max_holding_rule(
        position_amt=Decimal("1"),
        position_open_time=open_time,
        max_hold_minutes=10,
        now=now,
    )
    assert new_open_time == open_time
    assert not should_close


def test_position_older_than_threshold_triggers():
    open_time = 1000.0
    now = 1000.0 + 11 * 60  # 11 minutes later
    new_open_time, should_close = evaluate_max_holding_rule(
        position_amt=Decimal("1"),
        position_open_time=open_time,
        max_hold_minutes=10,
        now=now,
    )
    assert new_open_time == open_time
    assert should_close


