/**
 * capture.js — 采集与格式化的纯逻辑
 *
 * 这个文件不依赖 Chrome API，可以：
 *   1. 被 popup 通过 <script> 引入；
 *   2. 被 chrome.scripting.executeScript 注入到页面里运行；
 *   3. 被 Node 直接 require 做单元测试。
 *
 * 暴露：window.__quickCapture(selector, attr)
 *       window.__format(items, fmt)
 *       window.captureLogic
 */
(function (root) {
  'use strict';

  /**
   * 从 document 中按选择器采集元素
   * @param {string|null} selector CSS 选择器；为空表示取当前选中文字
   * @param {string|null} attr     要取的属性名；为空则取文本
   * @param {Document} doc         便于测试时传入假 document
   * @returns {{items: Array<{text:string, tag:string, url?:string}>, mode:string}}
   */
  function collect(selector, attr, doc) {
    const d = doc || (typeof document !== 'undefined' ? document : null);
    if (!d) return { items: [], mode: 'none' };

    // 无选择器：取当前选中的文字
    if (!selector) {
      const sel = (typeof window !== 'undefined' && window.getSelection) ? String(window.getSelection()) : '';
      const items = sel.trim() ? [{ text: sel.trim(), tag: 'selection' }] : [];
      return { items, mode: 'selection' };
    }

    let nodes;
    try {
      nodes = d.querySelectorAll(selector);
    } catch (e) {
      throw new Error('Invalid CSS selector');
    }

    const items = [];
    nodes.forEach((node) => {
      let text;
      if (attr) {
        text = node.getAttribute(attr) || '';
        // 相对链接补全
        if (attr === 'href' && text && node.href) text = node.href;
      } else {
        text = (node.textContent || '').replace(/\s+/g, ' ').trim();
      }
      if (!text) return;   // 跳过空值
      const item = { text, tag: node.tagName ? node.tagName.toLowerCase() : '' };
      if (node.href && !attr) item.url = node.href;
      items.push(item);
    });
    return { items, mode: 'selector' };
  }

  /**
   * 把采集结果格式化为文本 / JSON / CSV
   * @param {Array} items
   * @param {'text'|'json'|'csv'} fmt
   */
  function format(items, fmt) {
    if (!Array.isArray(items) || !items.length) return '';

    if (fmt === 'json') {
      return JSON.stringify(items, null, 2);
    }

    if (fmt === 'csv') {
      // 关键：表头要覆盖所有记录出现过的键。
      // 只取第一条的键会漏列——比如第一条没有 url、后面有，就会整列丢失。
      const header = [];
      items.forEach((it) => {
        Object.keys(it).forEach((k) => {
          if (header.indexOf(k) === -1) header.push(k);
        });
      });
      const esc = (v) => {
        const s = String(v == null ? '' : v);
        return /[",\n]/.test(s) ? `"${s.replace(/"/g, '""')}"` : s;
      };
      const lines = [header.join(',')];
      items.forEach((it) => {
        lines.push(header.map((k) => esc(it[k])).join(','));
      });
      return lines.join('\n');
    }

    // 默认文本：每行一个，带序号
    return items
      .map((it, i) => {
        const base = `${i + 1}. ${it.text}`;
        return it.url && it.url !== it.text ? `${base}\n   ${it.url}` : base;
      })
      .join('\n');
  }

  const api = { collect, format };

  if (typeof module !== 'undefined' && module.exports) {
    module.exports = api;          // Node 测试用
  }
  if (root) {
    root.captureLogic = api;
    root.__quickCapture = function (selector, attr) {
      return api.collect(selector, attr, document);
    };
    root.__format = api.format;
  }
})(typeof window !== 'undefined' ? window : null);
