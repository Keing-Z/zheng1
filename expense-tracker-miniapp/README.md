# Expense Tracker — WeChat Mini Program

A mobile expense tracker designed around one constraint: **logging an expense must take
under three seconds.**

## Why that constraint

Expense apps rarely fail for lack of features — they fail because logging is slow, so users
abandon them within a week. Every design decision here follows from that observation.

## Screens

| Tab | What it does |
|---|---|
| **记一笔 (Log)** | Custom numeric keypad, category picker, optional note — one screen, no scrolling |
| **账单 (Bills)** | Records grouped by day, month switcher, category filter, long-press to delete |
| **报表 (Reports)** | Donut chart of spending by category, ranked breakdown, 6-month trend bars |
| **我的 (Settings)** | Monthly budget with over-spend highlighting, streak counter, achievements, backup |

## Design decisions

**A custom keypad instead of the system keyboard.** The text keyboard covers roughly half
the screen on a typical phone, which breaks the flow of a one-handed, few-second
interaction. A fixed keypad keeps the amount display and the categories visible at all
times.

**Auto-clear after saving.** When someone logs three expenses in a row (lunch, transport,
coffee), forcing them to clear the field three times adds friction for no benefit.

**The note field is optional.** Requiring text input is the single most common reason
people stop logging small transactions.

**Amounts stored as integer cents.** Floating-point arithmetic accumulates error in
financial contexts — `0.1 + 0.2` evaluates to `0.30000000000000004`. Every amount is stored
and summed as an integer number of cents, and formatted only at render time.

**Dates assembled in local time.** `Date.prototype.toISOString()` returns UTC, which in
UTC+8 shifts any entry made between midnight and 08:00 into the previous day. Dates are
built from local getters instead.

**Donut chart via CSS `conic-gradient`.** The requirement is a proportion ring, not a
general chart engine. Using `conic-gradient` avoids pulling in a canvas library and saves
roughly 30 KB of runtime dependency plus a repaint.

**Offline-first, no backend.** No account, no server, no cost, and no user data leaving
the device. Backup is an explicit JSON export rather than silent cloud sync.

## Testing

Three layers, **82 assertions**, all passing:

```bash
node test/store.test.js         # 26 — formatting, aggregation, streaks, budgets
node test/integration.test.js   # 42 — full interaction flows across all four pages
node test/static.test.js        #     — page registration, event bindings, template vars
```

The integration layer runs the real page logic against a mocked `wx` runtime, so keypad
edge cases (double decimal points, arcade limits, backspace at zero), filtering, month
rollover, deletion and budget states are all exercised without a device.

### Defects the tests found and fixed

1. **CSV export dropped a whole column.** The header was built from the first row's keys, so
   if row 1 lacked a field that later rows had, that column vanished from the export. Fixed
   by taking the union of keys across all rows.
2. **HTML text extraction returned children in reverse order.** The extractor concatenated
   an element's own text before its children's, so `<div><b>X</b> Y</div>` produced `"Y X"`.
   Fixed by keeping text fragments and child nodes in a single document-ordered sequence.
3. **Restoring a backup doubled the data.** Re-importing the same backup appended every
   record again. Fixed with ID-based de-duplication on merge.

## Structure

```
app.js / app.json / app.wxss     Global config and styles
pages/index/                     Log an expense
pages/bill/                      Bills list
pages/report/                    Charts
pages/mine/                      Budget, achievements, backup
utils/store.js                   Data layer and all business logic
test/                            Unit, integration and static tests
```

## Running it

Open the folder in WeChat DevTools and use a test AppID — no registration required to
preview locally.
