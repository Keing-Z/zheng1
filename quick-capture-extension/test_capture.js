/* capture.js 单元测试（Node 环境，用假 document 模拟页面） */
const assert = require('assert');
const { collect, format } = require('./capture.js');

let pass = 0, fail = 0;
function t(name, fn) {
  try { fn(); pass++; console.log('  OK   ' + name); }
  catch (e) { fail++; console.log('  FAIL ' + name + ' :: ' + e.message); }
}
const eq = (a, b) => assert.strictEqual(a, b);

/* ---------- 造一个假 DOM ---------- */
function node(tag, text, attrs = {}) {
  return {
    tagName: tag.toUpperCase(),
    textContent: text,
    href: attrs.href || undefined,
    getAttribute(name) { return attrs[name] !== undefined ? attrs[name] : null; }
  };
}

function fakeDoc(nodes) {
  return {
    querySelectorAll(sel) {
      if (sel === 'BAD[') throw new Error('syntax error');
      return nodes.filter(() => true);
    }
  };
}

console.log('【采集：按选择器取文本】');
const nodes = [node('h2', '  Widget   A  '), node('h2', 'Widget B')];
t('取到 2 条', () => eq(collect('h2', null, fakeDoc(nodes)).items.length, 2));
t('空白被规整', () => eq(collect('h2', null, fakeDoc(nodes)).items[0].text, 'Widget A'));
t('tag 为小写', () => eq(collect('h2', null, fakeDoc(nodes)).items[0].tag, 'h2'));
t('跳过空文本节点', () => {
  const r = collect('h2', null, fakeDoc([node('h2', '   '), node('h2', 'X')]));
  eq(r.items.length, 1);
});

console.log('【采集：按属性取】');
const links = [node('a', 'detail', { href: 'https://a.com/x' })];
t('取 href 属性', () => eq(collect('a', 'href', fakeDoc(links)).items[0].text, 'https://a.com/x'));
t('属性缺失时为空字符串', () => {
  const r = collect('a', 'title', fakeDoc([node('a', 'x', {})]));
  eq(r.items.length, 0, '空值应被跳过');
});

console.log('【采集：异常处理】');
t('非法选择器抛错', () => {
  assert.throws(() => collect('BAD[', null, fakeDoc([])), /Invalid CSS selector/);
});
t('没有 document 时安全返回空', () => {
  eq(collect('h2', null, null).items.length, 0);
});

console.log('【格式化：text】');
const items = [
  { text: 'A', tag: 'h2' },
  { text: 'B', tag: 'a', url: 'https://b.com' }
];
t('带序号', () => eq(format(items, 'text'), '1. A\n2. B\n   https://b.com'));
t('空数组返回空串', () => eq(format([], 'text'), ''));

console.log('【格式化：json】');
t('JSON 合法且可解析', () => {
  const out = format(items, 'json');
  const parsed = JSON.parse(out);
  eq(parsed.length, 2);
  eq(parsed[1].url, 'https://b.com');
});

console.log('【格式化：csv】');
t('含表头', () => eq(format(items, 'csv').split('\n')[0], 'text,tag,url'));
t('缺失字段留空', () => {
  const csv = format(items, 'csv').split('\n');
  eq(csv[1], 'A,h2,');
});
t('逗号和引号被正确转义', () => {
  const out = format([{ text: 'a,b "c"', tag: 'x' }], 'csv');
  assert.ok(out.includes('"a,b ""c"""'), out);
});

console.log(`\n结果：通过 ${pass} 项，失败 ${fail} 项`);
process.exit(fail ? 1 : 0);
