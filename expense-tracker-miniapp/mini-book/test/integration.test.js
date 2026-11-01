/* 集成测试：用假的 wx 环境跑四个页面，验证真实操作流程 */
const fs = require('fs');
const path = require('path');
const Module = require('module');

const root = path.resolve(__dirname, '..');

/* ---------- 1) 搭建假的 wx 环境 ---------- */
const storage = new Map();
const toasts = [];
let modalAnswer = true;

global.wx = {
  getStorageSync: (k) => (storage.has(k) ? JSON.parse(storage.get(k)) : ''),
  setStorageSync: (k, v) => storage.set(k, JSON.stringify(v)),
  removeStorageSync: (k) => storage.delete(k),
  showToast: (o) => toasts.push(o.title),
  showModal: (o) => { if (o.success) o.success({ confirm: modalAnswer, cancel: !modalAnswer }); },
  setClipboardData: (o) => { storage.set('__clip', JSON.stringify(o.data)); if (o.success) o.success(); },
  vibrateShort: () => {},
  getSystemInfoSync: () => ({ platform: 'devtools', windowWidth: 375 }),
};

/* ---------- 2) 假的 App / Page ---------- */
let appInstance = null;
global.App = (cfg) => { appInstance = cfg; };

let pageRegistry = [];
let currentCfg = null;
global.Page = (cfg) => { currentCfg = cfg; };

/** 创建一个页面实例：合并 data、绑定方法 */
function createPage(relPath) {
  global.getApp = () => appInstance;
  currentCfg = null;

  delete require.cache[require.resolve(path.join(root, relPath))];
  require(path.join(root, relPath));
  const cfg = currentCfg;

  const inst = {
    data: JSON.parse(JSON.stringify(cfg.data || {})),
    setData(patch, cb) {
      Object.assign(this.data, patch);
      if (cb) cb();
    },
  };
  Object.keys(cfg).forEach((k) => {
    if (typeof cfg[k] === 'function') inst[k] = cfg[k].bind(inst);
  });
  return inst;
}

/* ---------- 3) 加载 app.js（初始化） ---------- */
require(path.join(root, 'app.js'));
appInstance.onLaunch();

const S = require(path.join(root, 'utils', 'store.js'));

let pass = 0, fail = 0;
function t(name, fn) {
  try { fn(); pass++; console.log('  ✓ ' + name); }
  catch (e) { fail++; console.log('  ✗ ' + name + ' :: ' + e.message); }
}
const eq = (a, b, m) => { if (a !== b) throw new Error((m || '') + ` 期望 ${b}，实际 ${a}`); };

/* ================= 记账页 ================= */
console.log('\n【记账页 · 真实操作流程】');
const idx = createPage('pages/index/index.js');
idx.onLoad();

t('初始金额为 0', () => eq(idx.data.displayAmount, '0'));
t('初始分类为餐饮', () => eq(idx.data.catId, 'food'));

// 模拟点击 1 2 3 . 5  → 123.5
['1', '2', '3', '.', '5'].forEach((k) =>
  idx.onKey({ currentTarget: { dataset: { k } } }));
t('键盘输入 123.5', () => eq(idx.data.displayAmount, '123.5'));

// 小数点只能有一个
idx.onKey({ currentTarget: { dataset: { k: '.' } } });
t('重复小数点被忽略', () => eq(idx.data.displayAmount, '123.5'));

// 小数位最多 2 位
idx.onKey({ currentTarget: { dataset: { k: '9' } } });
t('小数位最多 2 位', () => eq(idx.data.displayAmount, '123.59'));

// 退格
idx.onKey({ currentTarget: { dataset: { k: 'del' } } });
t('退格生效', () => eq(idx.data.displayAmount, '123.5'));

// 清空
idx.onKey({ currentTarget: { dataset: { k: 'clear' } } });
t('清空后回到 0', () => eq(idx.data.displayAmount, '0'));

// 选分类 + 填备注 + 保存
idx.onKey({ currentTarget: { dataset: { k: '5' } } });
idx.onKey({ currentTarget: { dataset: { k: '0' } } });
idx.onPickCat({ currentTarget: { dataset: { id: 'traffic' } } });
idx.onNoteInput({ detail: { value: '坐地铁去上课' } });
idx.onSave();

const recs = S.readRecords();
t('保存后记录数为 1', () => eq(recs.length, 1));
t('金额按分存储（5000）', () => eq(recs[0].amount, 5000));
t('分类正确', () => eq(recs[0].catId, 'traffic'));
t('备注已保存', () => eq(recs[0].note, '坐地铁去上课'));
t('保存后金额归零（可连续记账）', () => eq(idx.data.displayAmount, '0'));
t('保存后备注清空', () => eq(idx.data.note, ''));
t('本月概览已刷新', () => eq(idx.data.monthTotalText, '50'));

// 金额为 0 时不能保存
const before = S.readRecords().length;
idx.onSave();
t('金额为 0 时拒绝保存', () => eq(S.readRecords().length, before));
t('并给出提示', () => eq(toasts[toasts.length - 1], '请输入金额'));

/* ================= 账单页 ================= */
console.log('\n【账单页】');
// 账单页是按“月”过滤的（按月对账的设计），所以测试数据必须落在同一个自然月内。
// 注意两个坑：
//   1) 不能用 Date.now()-86400000 推“昨天”——每月 1 日凌晨会落到上个月；
//   2) 今天是 1 号时，“昨天”本来就不在本月，无法同时测“今天/昨天”分组。
// 因此这里统一取「本月内在今天之前的一天」，保证任何日期跑测试都稳定。
const todayKeyNow = S.ymd(new Date());
const siblingDate = (() => {
  const d = new Date();
  if (d.getDate() > 1) {
    d.setDate(d.getDate() - 1);   // 本月内，取昨天
    return d;
  }
  return d;                        // 1 号：本月内没有“昨天”，用今天兜底（见下方断言适配）
})();
const siblingKey = S.ymd(siblingDate);
const hasPrevInMonth = siblingKey !== todayKeyNow;
S.addRecord({ type: 'expense', amount: 1234, catId: 'food', note: '午饭', date: siblingKey });
S.addRecord({ type: 'expense', amount: 10000, catId: 'study', note: '买书', date: siblingKey });

const expectGroupCount = hasPrevInMonth ? 2 : 1;   // 1 号时两组会合并成一组

const bill = createPage('pages/bill/bill.js');
bill.onLoad();
bill.onShow();

t('按日分组组数正确', () => eq(bill.data.groups.length, expectGroupCount));
t('首组是今天', () => eq(bill.data.groups[0].dayLabel, '今天'));
if (hasPrevInMonth) {
  t('昨天标签正确', () => eq(bill.data.groups[1].dayLabel, '昨天'));
  t('昨天合计 112.34', () => eq(bill.data.groups[1].totalText, '112.34'));
}
t('本月汇总笔数 3', () => eq(bill.data.monthCount, 3));

// 分类筛选
bill.onFilter({ currentTarget: { dataset: { id: 'food' } } });
t('筛选餐饮后只剩 1 组', () => eq(bill.data.groups.length, 1));
t('筛选后合计 12.34', () => eq(bill.data.groups[0].totalText, '12.34'));
bill.onFilter({ currentTarget: { dataset: { id: '' } } });
t('取消筛选恢复全部组', () => eq(bill.data.groups.length, expectGroupCount));

// 月份切换
const now = new Date();
bill.onPrev();
const expectM = now.getMonth() === 0 ? 12 : now.getMonth();
t('上一月切换正确', () => eq(bill.data.m, expectM));

// 删除：删掉那条“买书”（学习类），保留餐饮类，避免影响后面“今天是否已记”的断言
const studyId = S.readRecords().find((r) => r.catId === 'study').id;
bill.onDelete({ currentTarget: { dataset: { id: studyId } } });
t('长按删除生效', () => eq(S.readRecords().length, 2));

/* ================= 报表页 ================= */
console.log('\n【报表页】');
const rep = createPage('pages/report/report.js');
rep.onLoad();
rep.onShow();

const repTotalCents = S.readRecords()
  .filter((r) => r.date && r.date.slice(0, 7) === S.ymd(new Date()).slice(0, 7))
  .reduce((s, r) => s + r.amount, 0);
t('总额与数据一致', () => eq(rep.data.totalText, S.yuan(repTotalCents)));
t('分类占比合计≈100', () => {
  const s = rep.data.byCat.reduce((a, c) => a + c.pct, 0);
  if (Math.abs(s - 100) > 0.5) throw new Error('占比=' + s);
});
// 分类数量按“本月实际存在的分类”动态校验，不再写死，
// 因为前面的删除步骤已经改变了数据集，且月初时“昨天”那条可能属于上个月。
t('分类数量与数据一致', () => {
  const expectCats = new Set(
    S.readRecords()
      .filter((r) => r.date && r.date.slice(0, 7) === S.ymd(new Date()).slice(0, 7))
      .map((r) => r.catId)
  ).size;
  eq(rep.data.byCat.length, expectCats);
});
t('分类按金额从高到低排序', () => {
  const amts = rep.data.byCat.map((c) => c.amount);
  for (let i = 1; i < amts.length; i++) {
    if (amts[i] > amts[i - 1]) throw new Error('排序错误：' + amts.join(','));
  }
});
t('环形图 CSS 已生成', () => {
  if (!rep.data.donutCss.startsWith('conic-gradient(')) throw new Error(rep.data.donutCss);
});
t('趋势返回 6 个月', () => eq(rep.data.trend.length, 6));
t('柱高在 0-100 之间', () => {
  rep.data.trend.forEach((x) => {
    if (x.h < 0 || x.h > 100) throw new Error(x.label + ' h=' + x.h);
  });
});

/* ================= 我的页 ================= */
console.log('\n【我的页】');
const mine = createPage('pages/mine/mine.js');
mine.onShow();

t('记录总数 2', () => eq(mine.data.totalRecords, 2));
t('连续天数正确（今天为起点）', () => eq(mine.data.streakDays, hasPrevInMonth ? 2 : 1));
t('今天已记', () => eq(mine.data.todayDone, true));

// 设置预算（用当前实际支出作为基准，避免断言写死）
const curRecords = S.readRecords();
const curNow = new Date();
const curSum = S.summaryMonth(curRecords, curNow.getFullYear(), curNow.getMonth() + 1);
const spentYuan = curSum.total / 100;
const budgetYuan = Math.max(1, spentYuan - 10);   // 故意设成比支出少 10 元 → 必然超支

mine.onBudgetInput({ detail: { value: String(budgetYuan) } });
mine.onSaveBudget();
t('预算保存（分）', () => eq(S.readSettings().budget, Math.round(budgetYuan * 100)));
t('已超预算', () => eq(mine.data.budget.level, 'over'));
t('超支金额 = 支出 - 预算', () => eq(mine.data.overText, S.yuan(Math.round((spentYuan - budgetYuan) * 100))));
t('进度条封顶 100', () => eq(mine.data.barWidth, 100));

// 清除预算
mine.onBudgetInput({ detail: { value: '' } });
mine.onSaveBudget();
t('可清除预算', () => eq(S.readSettings().budget, 0));

// 成就
t('成就列表非空', () => { if (!mine.data.achList.length) throw new Error('空'); });
t('首笔成就已解锁', () => {
  const a = mine.data.achList.find((x) => x.id === 'first');
  if (!a.unlocked) throw new Error('未解锁');
});

// 导出
mine.onExport();
t('导出写入剪贴板', () => {
  const clip = storage.get('__clip');
  const data = JSON.parse(JSON.parse(clip));
  if (!data.records || data.records.length !== 2) throw new Error('导出数据不对');
});

/* ================= 结果 ================= */
console.log(`\n结果：通过 ${pass} 项，失败 ${fail} 项`);
process.exit(fail ? 1 : 0);
