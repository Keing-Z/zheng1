/* 单元测试：验证 store.js 的核心算法（不依赖微信环境） */
const assert = require('assert');
const S = require('../utils/store.js');

let pass = 0, fail = 0;
function t(name, fn) {
  try { fn(); pass++; console.log('  ✓ ' + name); }
  catch (e) { fail++; console.log('  ✗ ' + name + ' :: ' + e.message); }
}

// 构造测试数据：2026-10
const NOW = new Date(2026, 9, 28); // 2026-10-28
const rec = (date, amount, catId = 'food', extra = {}) => ({
  id: 'x' + Math.random(), type: 'expense', amount, catId, note: '', date, ts: 0, ...extra
});

console.log('【金额格式化】');
t('15000 分 → 150', () => assert.strictEqual(S.yuan(15000), '150'));
t('1234 分 → 12.34', () => assert.strictEqual(S.yuan(1234), '12.34'));
t('0 分 → 0', () => assert.strictEqual(S.yuan(0), '0'));

console.log('【月度汇总】');
const oct = [
  rec('2026-10-01', 10000, 'food'),
  rec('2026-10-02', 5000, 'food'),
  rec('2026-10-03', 3000, 'traffic'),
  rec('2026-09-30', 99999, 'food'),   // 上个月，不应计入
];
t('总额正确', () => assert.strictEqual(S.summaryMonth(oct, 2026, 10).total, 18000));
t('笔数正确', () => assert.strictEqual(S.summaryMonth(oct, 2026, 10).count, 3));
t('分类排序：餐饮第一', () => {
  const r = S.summaryMonth(oct, 2026, 10);
  assert.strictEqual(r.byCat[0].catId, 'food');
  assert.strictEqual(r.byCat[0].amount, 15000);
});
t('分类占比合计≈100%', () => {
  const r = S.summaryMonth(oct, 2026, 10);
  const sum = r.byCat.reduce((s, c) => s + c.pct, 0);
  assert.ok(Math.abs(sum - 100) < 0.5, '占比=' + sum);
});
t('日均按已过天数算', () => {
  const r = S.summaryMonth(oct, 2026, 10);
  // 动态推算应得的天数，避免把“今天”写死导致测试过期：
  // 本月进行中 → 按今天几号；本月已过 → 按整月天数。
  const today = new Date();
  const cur = new Date(today.getFullYear(), today.getMonth(), 1);
  const target = new Date(2026, 9, 1);
  let elapsed;
  if (cur.getTime() === target.getTime()) elapsed = today.getDate();
  else if (cur > target) elapsed = 31;      // 2026-10 已整月过去
  else elapsed = 31;                        // 尚未到来时按整月口径
  assert.strictEqual(r.avgPerDay, Math.round(18000 / elapsed));
});
t('空数据不报错', () => {
  const r = S.summaryMonth([], 2026, 10);
  assert.strictEqual(r.total, 0);
  assert.strictEqual(r.byCat.length, 0);
});

console.log('【趋势】');
const trend = S.trendMonths(oct, 6, NOW);
t('返回 6 个月', () => assert.strictEqual(trend.length, 6));
t('最后一个月是 10 月', () => assert.strictEqual(trend[5].m, 10));
t('10 月总额 180 元', () => assert.strictEqual(trend[5].total, 18000));

console.log('【按日分组】');
const g = S.groupByDay([
  rec('2026-10-28', 1000),
  rec('2026-10-28', 2000),
  rec('2026-10-27', 500),
], NOW);
t('分 2 组', () => assert.strictEqual(g.length, 2));
t('今天标签', () => assert.strictEqual(g[0].dayLabel, '今天'));
t('昨天标签', () => assert.strictEqual(g[1].dayLabel, '昨天'));
t('今天合计 30 元', () => assert.strictEqual(g[0].total, 3000));

console.log('【连续天数】');
t('今天没记、昨天记了 → 从昨天算起', () => {
  const r = S.streak([rec('2026-10-27', 100), rec('2026-10-26', 100)], NOW);
  assert.strictEqual(r.days, 2);
  assert.strictEqual(r.todayDone, false);
});
t('今天记了 → 今天计入', () => {
  const r = S.streak([rec('2026-10-28', 100), rec('2026-10-27', 100)], NOW);
  assert.strictEqual(r.days, 2);
  assert.strictEqual(r.todayDone, true);
});
t('中间断一天就中断', () => {
  const r = S.streak([rec('2026-10-28', 1), rec('2026-10-26', 1)], NOW);
  assert.strictEqual(r.days, 1);
});
t('空数据为 0', () => assert.strictEqual(S.streak([], NOW).days, 0));

console.log('【预算】');
t('未设预算 level=none', () => assert.strictEqual(S.budgetStatus(0, 5000).level, 'none'));
t('超支 over=true', () => {
  const r = S.budgetStatus(100000, 120000);
  assert.strictEqual(r.over, true);
  assert.strictEqual(r.level, 'over');
  assert.strictEqual(r.remain, -20000);
});
t('80% 警告', () => assert.strictEqual(S.budgetStatus(100000, 85000).level, 'warn'));
t('正常 ok', () => assert.strictEqual(S.budgetStatus(100000, 10000).level, 'ok'));

console.log('【成就】');
t('第一笔解锁', () => {
  const a = S.achievements([rec('2026-10-28', 100)]);
  const first = a.find((x) => x.id === 'first');
  assert.strictEqual(first.unlocked, true);
});
t('未达成不把进度算成负数/超 100', () => {
  const a = S.achievements([]);
  a.forEach((x) => {
    assert.ok(x.progress >= 0 && x.progress <= 100, x.id + ' 进度越界 ' + x.progress);
  });
});

console.log(`\n结果：通过 ${pass} 项，失败 ${fail} 项`);
process.exit(fail ? 1 : 0);
