/* 备份导出 / 恢复 的单元测试 */
const assert = require('assert');

// 假的 wx 存储环境
const storage = new Map();
global.wx = {
  getStorageSync: (k) => (storage.has(k) ? JSON.parse(storage.get(k)) : ''),
  setStorageSync: (k, v) => storage.set(k, JSON.stringify(v)),
};

const S = require('../utils/store.js');

let pass = 0, fail = 0;
function t(name, fn) {
  try { fn(); pass++; console.log('  ✓ ' + name); }
  catch (e) { fail++; console.log('  ✗ ' + name + ' :: ' + e.message); }
}

const rec = (date, amount, catId = 'food', extra = {}) => ({
  id: 'x' + Math.random().toString(36).slice(2), type: 'expense',
  amount, catId, note: '', date, ts: Date.now(), ...extra
});

console.log('【导出】');
S.writeRecords([rec('2026-11-01', 1000), rec('2026-11-02', 2500, 'traffic')]);
const bk = S.buildBackup();
t('备份是合法 JSON', () => { JSON.parse(bk); });
t('备份带版本号', () => assert.strictEqual(JSON.parse(bk).v, 1));
t('备份包含全部记录', () => assert.strictEqual(JSON.parse(bk).records.length, 2));

console.log('【恢复：正常情况】');
const parsed = S.parseBackup(bk);
t('解析成功', () => assert.strictEqual(parsed.ok, true));
t('解析出 2 条', () => assert.strictEqual(parsed.records.length, 2));

console.log('【恢复：重复导入不产生双倍数据】');
const merged1 = S.mergeRecords(parsed.records);
t('重复导入新增 0 条', () => assert.strictEqual(merged1.added, 0));
t('重复导入全部跳过', () => assert.strictEqual(merged1.skipped, 2));
t('总数仍为 2', () => assert.strictEqual(merged1.total, 2));

console.log('【恢复：新数据合并】');
const extra = parseAndCheck(JSON.stringify({ v: 1, records: [rec('2026-11-03', 500, 'study')] }));
t('新记录可合并', () => {
  const m = S.mergeRecords(extra);
  assert.strictEqual(m.added, 1);
  assert.strictEqual(m.total, 3);
});

console.log('【恢复：异常输入】');
const bad = [
  ['空字符串', '', '没有读到备份内容'],
  ['null', null, '没有读到备份内容'],
  ['非 JSON 文本', '这是一段普通文字', '内容不是有效的备份格式'],
  ['JSON 但无 records', '{"foo":1}', '备份里没有找到记录'],
  ['records 不是数组', '{"records":"abc"}', '备份里没有找到记录'],
];
bad.forEach(([name, input, expectReason]) => {
  t(`拒绝：${name}`, () => {
    const r = S.parseBackup(input);
    assert.strictEqual(r.ok, false);
    assert.strictEqual(r.reason, expectReason);
  });
});

console.log('【恢复：脏数据逐条过滤】');
t('丢弃金额为 0 / 负数 / 非数字的记录', () => {
  const txt = JSON.stringify({
    records: [
      { amount: 0, date: '2026-11-01' },
      { amount: -100, date: '2026-11-01' },
      { amount: 'abc', date: '2026-11-01' },
      { amount: 100, date: '2026-11-01' },   // 唯一合法的
    ]
  });
  const r = S.parseBackup(txt);
  assert.strictEqual(r.ok, true);
  assert.strictEqual(r.records.length, 1);
});
t('丢弃日期格式错误的记录', () => {
  const txt = JSON.stringify({ records: [{ amount: 100, date: '2026/11/01' }] });
  const r = S.parseBackup(txt);
  assert.strictEqual(r.ok, false);
});
t('未知分类归入「其他」', () => {
  const txt = JSON.stringify({ records: [{ amount: 100, date: '2026-11-01', catId: '不存在' }] });
  const r = S.parseBackup(txt);
  assert.strictEqual(r.records[0].catId, 'other');
});
t('缺少 id 时自动补一个', () => {
  const txt = JSON.stringify({ records: [{ amount: 100, date: '2026-11-01' }] });
  const r = S.parseBackup(txt);
  assert.ok(r.records[0].id && typeof r.records[0].id === 'string');
});
t('金额保留为整数分', () => {
  const txt = JSON.stringify({ records: [{ amount: 12.7, date: '2026-11-01' }] });
  const r = S.parseBackup(txt);
  assert.strictEqual(r.records[0].amount, 13);
});

function parseAndCheck(txt) {
  const r = S.parseBackup(txt);
  assert.strictEqual(r.ok, true);
  return r.records;
}

console.log(`\n结果：通过 ${pass} 项，失败 ${fail} 项`);
process.exit(fail ? 1 : 0);
