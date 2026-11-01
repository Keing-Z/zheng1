# Portfolio Project 2 — Quick Capture (Chrome Extension)

A Manifest V3 extension that captures structured data from the current page and copies it
to the clipboard as text, JSON, or CSV — one click, no setup.

## Why it matters

Copying data by hand from a web page is slow and error-prone. This turns any page into
structured output in one action, with no backend, no tracking, and no external requests.

## Install (for testing)

1. Open `chrome://extensions`
2. Enable **Developer mode** (top right)
3. Click **Load unpacked** and select this folder
4. Pin the extension, open any website, click the icon

## Features

| Feature | Detail |
|---|---|
| Presets | Headings (h1–h3), links, first table's rows, current selection |
| Custom selector | Any CSS selector, optionally reading an attribute (`href`, `src`, `title`…) |
| Output formats | Plain text (numbered), JSON, CSV |
| CSV correctness | Header unions **all** keys across rows — no column silently dropped |
| CSV escaping | Commas, quotes and newlines are properly quoted for Excel/Sheets |
| Link handling | Absolute `href` is used when available |
| Preview | See the result before copying |

## Architecture

```
manifest.json     Manifest V3, minimal permissions
popup.html/.css   UI (340px popup)
popup.js          Popup logic — activates the tab, injects, formats
capture.js        Pure capture + format logic (no Chrome APIs)
test_capture.js   14 unit tests, run with plain Node
```

`capture.js` is deliberately free of Chrome APIs so it can be unit-tested in Node without
a browser:

```bash
node test_capture.js
```

## Tests

- 14 checks covering text/attribute extraction, whitespace normalisation, empty-node
  skipping, invalid-selector handling, and all three output formats
- **A real bug these caught:** the CSV header was built from the first row's keys only.
  If row 1 had no `url` but later rows did, that entire column vanished from the export.
  Fixed by taking the union of keys across all rows.

## Permissions (and why)

- `activeTab` — read only the page the user clicks on, not all sites
- `scripting` — inject the capture script into that page
- `clipboardWrite` — copy the result
- `storage` — reserved for remembering the last used preset

No network permissions. The extension never sends data anywhere.
