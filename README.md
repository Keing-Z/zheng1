# Hi, I'm KeingZheng — Data Science & Automation

Undergraduate in **Data Science and Big Data Technology** at Fujian Agriculture and Forestry
University (top 20% of major). I build things end-to-end: from data collection and cleaning
to models, interfaces, and tests.

This repository collects four projects I have built. Each one is complete — running code,
tests where applicable, and documentation of the design decisions behind it.

---

## Projects

### 1. [Mushroom Toxicity Classification](./mushroom-classification) — Python · scikit-learn
End-to-end machine-learning workflow on the UCI Mushroom dataset: exploratory analysis,
six-model benchmark under 5-fold cross-validation, and a three-method feature-importance
comparison (Random Forest importance, chi-square, mutual information).

**Why it's worth a look:** almost every model reaches 100% accuracy on this dataset, and
rather than reporting that as a win, the README explains *why* — the `odor` feature alone
carries mutual information of 1.0 — and moves the analysis to where it is actually
informative. Includes an interactive Chart.js dashboard.

`706-line pipeline · 6 models · 11 figures · full written report`

---

### 2. [Expense Tracker Mini Program](./expense-tracker-miniapp) — JavaScript · WeChat
A mobile expense tracker built around a single constraint: **logging an expense must take
under three seconds**. Every design choice follows from that — a custom numeric keypad
instead of the system keyboard, auto-clearing after save, note field optional.

Offline-first, no backend, no account, no server cost. Amounts stored as integer cents to
avoid floating-point drift; dates assembled in local time to avoid UTC offset bugs.

`4 pages · 82 automated assertions across unit, integration and static layers`

Three real defects were found by those tests and fixed — a CSV column being silently
dropped, HTML text extraction returning children in the wrong order, and backup restore
duplicating records. Each is documented in the project README.

---

### 3. [Web Scraper](./web-scraper) — Python (standard library only)
Turns a paginated listing page into clean CSV. **Zero third-party dependencies** — built on
`urllib` and `html.parser` alone, because in real client environments `pip install`
frequently fails behind proxies or with conflicting versions.

Implements a lightweight DOM tree, a CSS-selector subset (`tag`, `.class`, `#id`,
`[attr=value]`, descendant combinators), field mapping, retry with backoff, rate limiting,
and UTF-8 BOM output so Excel opens the result without mojibake.

`26 unit tests · end-to-end verified`

---

### 4. [Quick Capture — Chrome Extension](./quick-capture-extension) — Manifest V3
One click to capture structured data from the current page as text, JSON, or CSV. Built
with a deliberate split: all capture and formatting logic lives in a module with no Chrome
API dependency, so it is unit-testable in Node without launching a browser.

No network permissions. The extension never uploads anything.

`14 unit tests`

---

## What I care about

- **Explaining the "why".** A design decision without a stated trade-off is a guess.
  Every project README here says what was chosen, what was given up, and what I would
  change next.
- **Tests that find real bugs.** The three defects fixed in the expense tracker were not
  theoretical — they were caught by assertions I wrote, and each one had already broken
  something that a user would have noticed.
- **Honest reporting.** Where a result is unimpressive or a limitation is known, it is
  written down rather than omitted. See the mushroom project's accuracy discussion and the
  label-encoding limitation noted in the same README.

---

## Skills

| Area | Tools |
|---|---|
| Languages | Python, JavaScript, HTML/CSS, SQL |
| Data science | pandas, NumPy, scikit-learn, Matplotlib, Seaborn |
| Web & UI | Vanilla JS, Chrome Extension APIs, WeChat Mini Program, Chart.js |
| Practice | Git, automated testing, technical writing (Chinese and English) |

---

## Contact

- GitHub: [@Keing-Z](https://github.com/Keing-Z)
- Email: 2776599149@qq.com

---

<sub>The `docs/` folder holds application materials (resume) and, in Chinese, the walkthrough
used to publish this repository. English translations of each project README are included
alongside the Chinese originals where applicable.</sub>
