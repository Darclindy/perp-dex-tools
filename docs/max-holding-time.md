## Max holding time rule

This bot supports an optional **max holding time** rule that can automatically
close and reopen positions when they have been held for too long.

### CLI parameter

- `--max-hold-minutes`: maximum holding time for a position in **minutes**.  
  - `0` (default) disables the rule.
  - A positive value enables the rule. For example, `--max-hold-minutes 30`
    will force-close and reopen positions that have been held for 30 minutes
    or longer.

### Behaviour

- The bot continuously tracks when the current net position becomes non-zero.
- If the position remains non-zero longer than `max-hold-minutes`:
  - All existing close (take-profit) orders are cancelled.
  - The current net position is closed using a market order in the
    **close direction** (`close_order_side`).
  - A new grid position is opened using the existing `_place_and_monitor_open_order`
    logic, so the behaviour remains consistent with the current strategy.

If you do not want any time-based constraint on your positions, leave the
parameter at its default (`0`).


