# Portfolio Project 1 — Web Scraper (zero dependencies)

A configurable scraper that turns a listing page into clean CSV — **using only the Python
standard library**, so there is nothing to install on the client's machine.

## Why it matters

Most scrapers break when a client runs them: `pip install` fails behind a proxy, or a
dependency conflicts with their existing environment. This one runs on a bare Python
install — `python csv_scraper.py …` and it works.

## Usage

```bash
python csv_scraper.py \
  --url "https://example.com/list" \
  --row "div.item" \
  --field "name=h2" \
  --field "price=.price" \
  --field "link=a@href" \
  --out result.csv
```

Pagination:

```bash
--pages 5            # fetch page=1..5
--page-param page    # the query parameter the site uses
```

Authenticated pages:

```bash
--cookie "sessionid=abc123"
```

## Features

| Feature | Detail |
|---|---|
| Zero install | Only `urllib` + `html.parser` from the standard library |
| CSS selector subset | `tag`, `.class`, `#id`, `[attr=value]`, descendant combos (`div.item h2`) |
| Field mapping | `name=selector` for text, `name=selector@attr` for attributes |
| Link resolution | Relative `href`/`src` are resolved against the page URL |
| Robustness | 3 retries with backoff on network errors; per-page rate limiting |
| Encoding | Detects charset from headers; UTF-8 BOM output so Excel opens it correctly |

## Tests

```bash
python test_scraper.py
```

- 26 checks, no external dependencies
- Covers HTML parsing, text extraction order, selector matching, field definitions,
  pagination URL building, and malformed selectors

**A bug these tests caught:** an early version concatenated an element's own text before
its children's text, so `<div><b>X</b> Y</div>` produced `"Y X"` — the text order was
reversed. The fix keeps text fragments and child nodes in document order.

## How I'd adapt this for your site

1. You send me one page of HTML (or the URL).
2. I write the selectors against your actual structure.
3. You get the script plus a 5-line README — including exactly which lines to change if
   the site's layout changes later.
