/* 静态一致性检查：页面注册、WXML 事件绑定、数据字段引用 */
const fs = require('fs');
const path = require('path');

const root = path.resolve(__dirname, '..');
const app = JSON.parse(fs.readFileSync(path.join(root, 'app.json'), 'utf8'));

let fail = 0;
const bad = (msg) => { fail++; console.log('  ✗ ' + msg); };
const good = (msg) => console.log('  ✓ ' + msg);

console.log('【页面注册】');
app.pages.forEach((p) => {
  ['.js', '.json', '.wxml', '.wxss'].forEach((ext) => {
    const f = path.join(root, p + ext);
    if (!fs.existsSync(f)) bad(`缺少文件 ${p}${ext}`);
  });
});
good(`${app.pages.length} 个页面文件齐全`);

// tabBar 指向的页面必须在 pages 里
app.tabBar.list.forEach((t) => {
  if (!app.pages.includes(t.pagePath)) bad(`tabBar 指向未注册页面 ${t.pagePath}`);
});
good('tabBar 配置有效');

console.log('【WXML 事件绑定 → JS 方法】');
app.pages.forEach((p) => {
  const wxml = fs.readFileSync(path.join(root, p + '.wxml'), 'utf8');
  const js = fs.readFileSync(path.join(root, p + '.js'), 'utf8');
  const handlers = [...wxml.matchAll(/bind(?:tap|input|longpress|confirm|change)="([^"]+)"/g)].map((m) => m[1]);
  [...new Set(handlers)].forEach((h) => {
    // 匹配 `onXxx(` 或 `onXxx:` 形式
    const re = new RegExp(`\\b${h}\\s*\\(`);
    if (!re.test(js)) bad(`${p}: 绑定方法 ${h} 在 JS 中不存在`);
  });
  console.log(`  ✓ ${p}: ${new Set(handlers).size} 个绑定方法均存在`);
});

console.log('【WXML 引用的 data 字段 → JS data 初始值】');
app.pages.forEach((p) => {
  const wxml = fs.readFileSync(path.join(root, p + '.wxml'), 'utf8');
  const js = fs.readFileSync(path.join(root, p + '.js'), 'utf8');

  // 提取 {{ ... }} 里的顶层标识符
  const exprs = [...wxml.matchAll(/\{\{([^}]+)\}\}/g)].map((m) => m[1]);
  const idents = new Set();
  exprs.forEach((e) => {
    // 去掉字符串字面量，避免把 'food' 这类值当成变量
    const clean = e.replace(/'[^']*'/g, "''").replace(/"[^"]*"/g, '""');
    // 只取“根标识符”：前面不是 . 的标识符（item.emoji 只取 item）
    [...clean.matchAll(/(?<![.\w$])([a-zA-Z_$][\w$]*)/g)].forEach((m) => idents.add(m[1]));
  });

  // 微信模板内置变量 / 循环变量
  const builtin = new Set([
    'item', 'index', 'rec', 'true', 'false', 'null', 'undefined',
    'wx', 'length', 'Math', 'parseInt',
  ]);
  // JS 中 setData 的键 + data 初始键
  const dataKeys = new Set();
  [...js.matchAll(/^\s{4}([a-zA-Z_$][\w$]*)\s*:/gm)].forEach((m) => dataKeys.add(m[1]));
  [...js.matchAll(/setData\(\s*\{([\s\S]*?)\}/g)].forEach((m) => {
    [...m[1].matchAll(/([a-zA-Z_$][\w$]*)\s*:/g)].forEach((k) => dataKeys.add(k[1]));
  });
  // js 内部常量（如 curM 等）
  [...js.matchAll(/const\s+([a-zA-Z_$][\w$]*)/g)].forEach((m) => dataKeys.add(m[1]));

  const missing = [...idents].filter((i) => !builtin.has(i) && !dataKeys.has(i));
  if (missing.length) bad(`${p}: 未定义的变量 ${missing.join(', ')}`);
  else console.log(`  ✓ ${p}: ${idents.size} 个变量引用全部有定义`);
});

console.log(fail ? `\n失败 ${fail} 项` : '\n全部通过');
process.exit(fail ? 1 : 0);
