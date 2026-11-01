/* Quick Capture — popup logic
 * 把“采集页面数据”这段纯函数抽到 capture.js，
 * 这样可以直接在 Node 里测试，不需要打开浏览器。
 */

const $ = (s) => document.querySelector(s);
const statusEl = $('#status');
const resultEl = $('#result');

/* ---------- 预设 ---------- */
const PRESETS = {
  headings: { selector: 'h1, h2, h3', attr: null },
  links: { selector: 'a[href]', attr: null },
  tables: { selector: 'table tr', attr: null },
  selected: { selector: null, attr: null },
  custom: { selector: null, attr: null }
};

/* ---------- UI 交互 ---------- */
$('#preset').addEventListener('change', (e) => {
  const isCustom = e.target.value === 'custom';
  $('#customWrap').classList.toggle('hidden', !isCustom);
});

function setStatus(msg, isErr = false) {
  statusEl.textContent = msg;
  statusEl.classList.toggle('err', isErr);
}

function getFormat() {
  return document.querySelector('input[name="fmt"]:checked').value;
}

/* ---------- 从页面采集 ---------- */
async function captureFromPage() {
  const preset = $('#preset').value;
  const cfg = PRESETS[preset] || {};
  let selector = cfg.selector;
  let attr = cfg.attr;

  if (preset === 'custom') {
    selector = $('#customSel').value.trim();
    attr = $('#customAttr').value.trim() || null;
    if (!selector) throw new Error('Please enter a CSS selector');
  }

  const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
  if (!tab || !tab.id) throw new Error('No active tab');

  // 先注入纯逻辑脚本，再调用它（注入需要手动指定 files，才能在页面里拿到 captureLogic）
  await chrome.scripting.executeScript({
    target: { tabId: tab.id },
    files: ['capture.js']
  });
  const [{ result }] = await chrome.scripting.executeScript({
    target: { tabId: tab.id },
    func: (sel, at) => window.__quickCapture(sel, at),
    args: [selector, attr]
  });
  return result;
}

async function run(copy) {
  try {
    const preset = $('#preset').value;

    // “选中文字”在 popup 里直接拿不到，交给页面脚本
    const data = await captureFromPage();
    if (!data || !data.items || !data.items.length) {
      throw new Error('Nothing found for this selector on the page');
    }

    const fmt = getFormat();
    const output = window.__format(data.items, fmt);

    resultEl.hidden = false;
    resultEl.textContent = output.length > 2000 ? output.slice(0, 2000) + '\n…(truncated)' : output;
    setStatus(`Captured ${data.items.length} item(s)`);

    if (copy) {
      await navigator.clipboard.writeText(output);
      setStatus(`Copied ${data.items.length} item(s) to clipboard`);
    }
  } catch (e) {
    setStatus(e.message || String(e), true);
  }
}

$('#capture').addEventListener('click', () => run(true));
$('#preview').addEventListener('click', () => run(false));
