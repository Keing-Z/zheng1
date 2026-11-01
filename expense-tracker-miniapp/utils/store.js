/**
 * store.js —— 数据层与业务算法
 *
 * 设计原则：
 * 1. 所有读写都走 wx.getStorageSync / wx.setStorageSync（本地，无后端）；
 * 2. 纯计算函数（汇总、连续天数、预算）不依赖 wx，方便单元测试；
 * 3. 数据格式统一为 { id, type, amount(分), catId, note, date('YYYY-MM-DD'), ts }
 */

const KEY_RECORDS = 'book.records';
const KEY_SETTINGS = 'book.settings';

/* ---------------- 分类定义 ---------------- */
const CATS = [
  { id: 'food',   name: '餐饮',   emoji: '🍚', color: '#f97316' },
  { id: 'traffic',name: '交通',   emoji: '🚌', color: '#0ea5e9' },
  { id: 'shop',   name: '购物',   emoji: '🛍️', color: '#ec4899' },
  { id: 'fun',    name: '娱乐',   emoji: '🎮', color: '#8b5cf6' },
  { id: 'study',  name: '学习',   emoji: '📚', color: '#10b981' },
  { id: 'daily',  name: '日用',   emoji: '🧴', color: '#14b8a6' },
  { id: 'med',    name: '医疗',   emoji: '💊', color: '#ef4444' },
  { id: 'house',  name: '房租',   emoji: '🏠', color: '#6366f1' },
  { id: 'phone',  name: '通讯',   emoji: '📱', color: '#06b6d4' },
  { id: 'other',  name: '其他',   emoji: '📦', color: '#94a3b8' }
];

const CAT_MAP = {};
CATS.forEach((c) => { CAT_MAP[c.id] = c; });

/* ---------------- 日期工具 ---------------- */
function pad(n) { return String(n).padStart(2, '0'); }

/** Date -> 'YYYY-MM-DD'（本地时区，避免 toISOString 的 UTC 偏移坑） */
function ymd(d) {
  return `${d.getFullYear()}-${pad(d.getMonth() + 1)}-${pad(d.getDate())}`;
}

/** 'YYYY-MM-DD' -> Date（本地零点） */
function parseYmd(s) {
  const [y, m, d] = String(s).split('-').map(Number);
  return new Date(y, m - 1, d);
}

function startOfDay(d) { return new Date(d.getFullYear(), d.getMonth(), d.getDate()); }
function addDays(d, n) { const x = new Date(d); x.setDate(x.getDate() + n); return x; }
function diffDays(a, b) { return Math.round((startOfDay(b) - startOfDay(a)) / 86400000); }

/** 某月第一天 */
function monthStart(y, m) { return new Date(y, m - 1, 1); }
/** 某月天数 */
function daysInMonth(y, m) { return new Date(y, m, 0).getDate(); }

/** 金额（分）-> 显示字符串，去掉多余的 .00 */
function yuan(cents) {
  const v = Math.round(Number(cents) || 0) / 100;
  return Number.isInteger(v) ? String(v) : v.toFixed(2);
}

/**
 * 图表用的短格式：>= 1 万显示「1.2万」，避免坐标轴太长
 */
function yuanShort(cents) {
  const v = Math.round(Number(cents) || 0) / 100;
  if (Math.abs(v) >= 10000) return (v / 10000).toFixed(1) + '万';
  return Number.isInteger(v) ? String(v) : v.toFixed(1);
}

/**
 * 环形图分段：把分类占比转成 CSS conic-gradient 的色段
 * 微信小程序支持 conic-gradient，用它画环形图不需要 canvas，兼容性好、性能高。
 * @param {Array} byCat summaryMonth 输出的 byCat
 * @returns {Array<{color, start, end}>}
 */
function donutSegments(byCat) {
  let acc = 0;
  return byCat.map((c) => {
    const start = acc;
    acc += c.pct;
    return { color: c.color, start: Math.round(start * 10) / 10, end: Math.round(acc * 10) / 10 };
  });
}

/* ---------------- 纯计算：汇总 ---------------- */

/**
 * 按月汇总
 * @param {Array} records 全部记录
 * @param {number} y 年
 * @param {number} m 月(1-12)
 * @returns {{total:number, count:number, byCat:Array, avgPerDay:number}}
 */
function summaryMonth(records, y, m) {
  const prefix = `${y}-${pad(m)}`;
  const list = records.filter((r) => r.date && r.date.slice(0, 7) === prefix && r.type !== 'income');
  const total = list.reduce((s, r) => s + (r.amount || 0), 0);

  const acc = {};
  list.forEach((r) => {
    const id = r.catId || 'other';
    if (!acc[id]) acc[id] = { catId: id, amount: 0, count: 0 };
    acc[id].amount += r.amount || 0;
    acc[id].count += 1;
  });

  const byCat = Object.values(acc).map((x) => {
    const cat = CAT_MAP[x.catId] || CAT_MAP.other;
    return {
      ...x,
      name: cat.name,
      emoji: cat.emoji,
      color: cat.color,
      pct: total > 0 ? Math.round((x.amount / total) * 1000) / 10 : 0
    };
  }).sort((a, b) => b.amount - a.amount);

  const today = new Date();
  const isCurrent = today.getFullYear() === y && today.getMonth() + 1 === m;
  const elapsed = isCurrent ? today.getDate() : daysInMonth(y, m);

  return {
    total,
    count: list.length,
    byCat,
    avgPerDay: elapsed > 0 ? Math.round(total / elapsed) : 0
  };
}

/**
 * 近 N 个月趋势（含本月）
 * @returns {Array<{y,m,label,total}>}
 */
function trendMonths(records, n = 6, now = new Date()) {
  const out = [];
  for (let i = n - 1; i >= 0; i--) {
    const d = new Date(now.getFullYear(), now.getMonth() - i, 1);
    const y = d.getFullYear();
    const m = d.getMonth() + 1;
    out.push({
      y,
      m,
      label: `${m}月`,
      total: summaryMonth(records, y, m).total
    });
  }
  return out;
}

/**
 * 按日分组（用于账单页）
 * @returns {Array<{date, dayLabel, total, items}>} 新→旧
 */
function groupByDay(records, now = new Date()) {
  const valid = records.filter((r) => r.date && r.amount > 0);
  const map = {};
  valid.forEach((r) => {
    (map[r.date] = map[r.date] || []).push(r);
  });

  const todayKey = ymd(now);
  const yKey = ymd(addDays(now, -1));

  return Object.keys(map)
    .sort((a, b) => (a < b ? 1 : -1))
    .map((date) => {
      const items = map[date].slice().sort((a, b) => (b.ts || 0) - (a.ts || 0));
      const d = parseYmd(date);
      let dayLabel = `${mLabel(d)}`;
      if (date === todayKey) dayLabel = '今天';
      else if (date === yKey) dayLabel = '昨天';
      const total = items.reduce((s, r) => s + (r.type === 'income' ? -r.amount : r.amount), 0);
      return { date, dayLabel, total, items };
    });
}

function mLabel(d) {
  const wd = ['日', '一', '二', '三', '四', '五', '六'][d.getDay()];
  return `${d.getMonth() + 1}月${d.getDate()}日 周${wd}`;
}

/**
 * 连续记账天数
 * 规则：从今天往前数，遇到没有记录的一天就中断；
 * 如果今天还没记，但昨天记了，仍算“已连续”到昨天（给用户留当天余量）。
 * @returns {{days:number, todayDone:boolean, lastDate:string|null}}
 */
function streak(records, now = new Date()) {
  const set = new Set(records.filter((r) => r.date && r.amount > 0).map((r) => r.date));
  if (!set.size) return { days: 0, todayDone: false, lastDate: null };

  const todayKey = ymd(now);
  const todayDone = set.has(todayKey);

  let cursor = todayDone ? startOfDay(now) : addDays(startOfDay(now), -1);
  let days = 0;
  // 如果连昨天都没有，直接为 0
  while (set.has(ymd(cursor))) {
    days++;
    cursor = addDays(cursor, -1);
  }

  const sorted = [...set].sort();
  return { days, todayDone, lastDate: sorted[sorted.length - 1] || null };
}

/**
 * 本月预算使用情况
 * @returns {{budget:number, spent:number, remain:number, pct:number, over:boolean, level:string}}
 */
function budgetStatus(budget, spent) {
  const b = Math.max(0, Number(budget) || 0);
  if (b <= 0) return { budget: 0, spent, remain: 0, pct: 0, over: false, level: 'none' };
  const pct = Math.round((spent / b) * 1000) / 10;
  const over = spent > b;
  return {
    budget: b,
    spent,
    remain: b - spent,
    pct,
    over,
    level: over ? 'over' : pct >= 80 ? 'warn' : 'ok'
  };
}

/**
 * 成就解锁判断（连续天数 + 总笔数）
 * @returns {Array<{id,title,desc,unlocked,progress}>}
 */
function achievements(records) {
  const s = streak(records);
  const totalCount = records.filter((r) => r.amount > 0).length;
  const list = [
    { id: 'first', title: '开始时记账', desc: '记下第一笔', need: Math.min(1, totalCount), goal: 1, cur: totalCount },
    { id: 's3', title: '三分钟热度', desc: '连续记账 3 天', goal: 3, cur: s.days },
    { id: 's7', title: '一周坚持', desc: '连续记账 7 天', goal: 7, cur: s.days },
    { id: 's30', title: '习惯养成', desc: '连续记账 30 天', goal: 30, cur: s.days },
    { id: 'c50', title: '小有积累', desc: '累计记录 50 笔', goal: 50, cur: totalCount },
    { id: 'c200', title: '账目清晰', desc: '累计记录 200 笔', goal: 200, cur: totalCount }
  ];
  return list.map((x) => ({
    id: x.id,
    title: x.title,
    desc: x.desc,
    goal: x.goal,
    cur: Math.max(0, x.cur),
    unlocked: x.cur >= x.goal,
    progress: Math.min(100, Math.round((x.cur / x.goal) * 100))
  }));
}

/* ---------------- 存储层（依赖 wx，测试时可替换） ---------------- */
const hasWx = typeof wx !== 'undefined' && typeof wx.getStorageSync === 'function';

function readRecords() {
  if (!hasWx) return [];
  const v = wx.getStorageSync(KEY_RECORDS);
  return Array.isArray(v) ? v : [];
}

function writeRecords(list) {
  if (hasWx) wx.setStorageSync(KEY_RECORDS, list);
}

function readSettings() {
  const dft = { budget: 0, firstOpen: Date.now() };
  if (!hasWx) return dft;
  const v = wx.getStorageSync(KEY_SETTINGS);
  return v && typeof v === 'object' ? { ...dft, ...v } : dft;
}

function writeSettings(s) {
  if (hasWx) wx.setStorageSync(KEY_SETTINGS, s);
}

function addRecord(rec) {
  const list = readRecords();
  const item = {
    id: `r${Date.now()}${Math.floor(Math.random() * 1000)}`,
    type: 'expense',
    amount: 0,
    catId: 'other',
    note: '',
    date: ymd(new Date()),
    ts: Date.now(),
    ...rec
  };
  list.push(item);
  writeRecords(list);
  return item;
}

function deleteRecord(id) {
  const list = readRecords().filter((r) => r.id !== id);
  writeRecords(list);
  return list;
}

function updateRecord(id, patch) {
  const list = readRecords().map((r) => (r.id === id ? { ...r, ...patch } : r));
  writeRecords(list);
  return list;
}

/* ---------------- 备份导出 / 恢复 ---------------- */

/**
 * 生成备份文本（用户复制到剪贴板）
 */
function buildBackup() {
  return JSON.stringify({
    app: 'mini-book',
    v: 1,
    exportedAt: Date.now(),
    records: readRecords()
  });
}

/**
 * 校验并解析备份文本
 * @param {string} text 用户粘贴/剪贴板中的文本
 * @returns {{ok:boolean, records:Array, reason?:string}}
 */
function parseBackup(text) {
  if (!text || typeof text !== 'string' || !text.trim()) {
    return { ok: false, records: [], reason: '没有读到备份内容' };
  }
  let obj;
  try {
    obj = JSON.parse(text.trim());
  } catch (e) {
    return { ok: false, records: [], reason: '内容不是有效的备份格式' };
  }
  if (!obj || typeof obj !== 'object') {
    return { ok: false, records: [], reason: '备份内容格式不正确' };
  }
  if (!Array.isArray(obj.records)) {
    return { ok: false, records: [], reason: '备份里没有找到记录' };
  }

  // 逐条校验，丢弃非法数据而不是整包失败
  const valid = [];
  obj.records.forEach((r) => {
    if (!r || typeof r !== 'object') return;
    const amount = Number(r.amount);
    if (!isFinite(amount) || amount <= 0) return;
    if (!r.date || !/^\d{4}-\d{2}-\d{2}$/.test(String(r.date))) return;
    const catId = CAT_MAP[r.catId] ? r.catId : 'other';
    valid.push({
      id: typeof r.id === 'string' && r.id ? r.id : `r${Date.now()}${Math.floor(Math.random() * 10000)}`,
      type: r.type === 'income' ? 'income' : 'expense',
      amount: Math.round(amount),
      catId,
      note: typeof r.note === 'string' ? r.note.slice(0, 100) : '',
      date: r.date,
      ts: Number(r.ts) || Date.now()
    });
  });

  if (!valid.length) {
    return { ok: false, records: [], reason: '备份中没有可用的记录' };
  }
  return { ok: true, records: valid };
}

/**
 * 导入记录：按 id 去重合并（避免重复导入造成双倍数据）
 * @param {Array} incoming parseBackup 返回的记录
 * @returns {{added:number, skipped:number, total:number}}
 */
function mergeRecords(incoming) {
  const existing = readRecords();
  const seen = new Set(existing.map((r) => r.id));
  let added = 0;
  incoming.forEach((r) => {
    if (seen.has(r.id)) return;
    seen.add(r.id);
    existing.push(r);
    added++;
  });
  writeRecords(existing);
  return { added, skipped: incoming.length - added, total: existing.length };
}

module.exports = {
  CATS,
  CAT_MAP,
  // 日期
  pad, ymd, parseYmd, startOfDay, addDays, diffDays, monthStart, daysInMonth, mLabel,
  // 格式化
  yuan, yuanShort,
  // 计算
  summaryMonth, trendMonths, groupByDay, streak, budgetStatus, achievements, donutSegments,
  // 存储
  readRecords, writeRecords, readSettings, writeSettings,
  addRecord, deleteRecord, updateRecord,
  // 备份
  buildBackup, parseBackup, mergeRecords
};
