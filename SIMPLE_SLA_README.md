# Simple SLA Worker Solution

## Problem Solved
- **Scheduler overload**: Single worker processing all tickets every minute
- **Email queue congestion**: Synchronous email sending blocking scheduler
- **No prioritization**: All milestones checked at same frequency

## Simple Solution
**3 separate workers** for each milestone:

```
50% Worker → Every 3 minutes → Less critical
75% Worker → Every 2 minutes → More critical  
100% Worker → Every 1 minute → Most critical
```

## How It Works

### 1. **Separate Workers**
- `check_50_percent_sla()` - Runs every 3 minutes
- `check_75_percent_sla()` - Runs every 2 minutes  
- `check_100_percent_sla()` - Runs every 1 minute

### 2. **Smart Filtering**
Each worker only processes tickets that:
- Haven't been notified for that milestone
- Are still open/in-progress
- Actually reached the milestone percentage

### 3. **Async Email Sending**
- All emails sent via background jobs
- No scheduler blocking
- Email queue handles delivery

## Benefits

✅ **Simple to understand** - 3 workers, 3 functions
✅ **No scheduler blocking** - Async email sending
✅ **Prioritized checking** - 100% checked most frequently
✅ **Reduced load** - Each worker processes fewer tickets
✅ **Easy to debug** - Clear separation of concerns

## Implementation

### 1. **Files Added**
- `sla_simple.py` - Main worker functions
- `sla_state.py` - State tracking (existing)

### 2. **Scheduler Updated**
```python
scheduler_events = {
    "cron": {
        "*/3 * * * *": ["...check_50_percent_sla"],  # Every 3 min
        "*/2 * * * *": ["...check_75_percent_sla"],  # Every 2 min  
        "* * * * *": ["...check_100_percent_sla"],   # Every 1 min
        "*/10 * * * *": ["...run_state_tracking"]    # Every 10 min
    }
}
```

### 3. **Deploy**
```bash
bench restart
```

## For Your 15min SLA Case

- **50% (7.5min)**: Checked every 3 minutes → Alert within 3 minutes
- **75% (11.25min)**: Checked every 2 minutes → Alert within 2 minutes
- **100% (15min)**: Checked every 1 minute → Alert within 1 minute

**Result**: No more email queue congestion, faster alerts for critical milestones.

## Monitoring

```python
# Check if workers are running
frappe.get_all('Scheduled Job Type', ['name', 'last_execution'])

# Check email queue
frappe.db.sql("SELECT COUNT(*) FROM `tabEmail Queue` WHERE status='Not Sent'")
```

## Rollback
Simply revert `hooks.py` to original single scheduler if needed.