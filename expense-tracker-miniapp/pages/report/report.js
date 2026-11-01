const S = require('../../utils/store.js');

Page({
  data: {
    y: 0,
    m: 0,
    curM: 0,
    curLabel: '',
    isFuture: false,
    total: 0,
    totalText: '0',
    count: 0,
    avgText: '0',
    byCat: [],
    donutCss: '#eef0f6',
    trend: [],
    maxText: '0'
  },

  onLoad() {
    const now = new Date();
    this.setData({ y: now.getFullYear(), m: now.getMonth() + 1, curM: now.getMonth() + 1 });
  },

  onShow() {
    if (!this.data.y) {
      const now = new Date();
      this.setData({ y: now.getFullYear(), m: now.getMonth() + 1, curM: now.getMonth() + 1 });
    }
    this.render();
  },

  onPrev() {
    let { y, m } = this.data;
    m -= 1;
    if (m < 1) { m = 12; y -= 1; }
    this.setData({ y, m }, () => this.render());
  },

  onNext() {
    if (this.data.isFuture) return;
    let { y, m } = this.data;
    m += 1;
    if (m > 12) { m = 1; y += 1; }
    this.setData({ y, m }, () => this.render());
  },

  render() {
    const { y, m } = this.data;
    const now = new Date();
    const isFuture = y > now.getFullYear() || (y === now.getFullYear() && m > now.getMonth() + 1);
    const records = S.readRecords();

    // 1) 本月汇总
    const sum = S.summaryMonth(records, y, m);
    const byCat = sum.byCat.map((c) => ({
      ...c,
      amountText: S.yuan(c.amount)
    }));

    // 2) 环形图：拼成 conic-gradient
    let donutCss = '#eef0f6';
    if (sum.total > 0 && byCat.length) {
      const segs = S.donutSegments(byCat);
      const parts = segs.map((s) => `${s.color} ${s.start}% ${s.end}%`);
      // 用最后一段补齐 100%，避免取整后出现空白缝隙
      donutCss = `conic-gradient(${parts.join(', ')}, #eef0f6 ${segs[segs.length - 1].end}% 100%)`;
    }

    // 3) 近 6 个月趋势
    const trendRaw = S.trendMonths(records, 6, new Date(y, m - 1, 1));
    const max = Math.max(...trendRaw.map((t) => t.total), 1);
    const trend = trendRaw.map((t) => ({
      label: t.label,
      m: t.m,
      total: t.total,
      short: t.total > 0 ? S.yuanShort(t.total) : '',
      h: Math.max(t.total > 0 ? 6 : 0, Math.round((t.total / max) * 100))
    }));

    this.setData({
      curLabel: `${y} 年 ${m} 月`,
      isFuture,
      total: sum.total,
      totalText: S.yuan(sum.total),
      count: sum.count,
      avgText: S.yuan(sum.avgPerDay),
      byCat,
      donutCss,
      trend,
      maxText: S.yuan(max === 1 && trendRaw.every((t) => t.total === 0) ? 0 : max)
    });
  }
});
