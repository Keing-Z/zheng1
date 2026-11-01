const S = require('../../utils/store.js');

Page({
  data: {
    cats: S.CATS,
    y: 0,
    m: 0,
    curLabel: '',
    isFuture: false,
    filterCat: '',
    monthTotalText: '0',
    monthCount: 0,
    groups: []
  },

  onLoad() {
    const now = new Date();
    this.setData({ y: now.getFullYear(), m: now.getMonth() + 1 });
  },

  onShow() {
    if (!this.data.y) {
      const now = new Date();
      this.setData({ y: now.getFullYear(), m: now.getMonth() + 1 });
    }
    this.render();
  },

  onFilter(e) {
    this.setData({ filterCat: e.currentTarget.dataset.id || '' }, () => this.render());
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
    const { y, m, filterCat } = this.data;
    const now = new Date();
    const isFuture = y > now.getFullYear() || (y === now.getFullYear() && m > now.getMonth() + 1);

    const all = S.readRecords();
    const prefix = `${y}-${String(m).padStart(2, '0')}`;
    let list = all.filter((r) => r.date && r.date.slice(0, 7) === prefix);
    if (filterCat) list = list.filter((r) => r.catId === filterCat);

    const sum = S.summaryMonth(list, y, m);
    const groups = S.groupByDay(list, now).map((g) => ({
      date: g.date,
      dayLabel: g.dayLabel,
      totalText: S.yuan(g.total),
      items: g.items.map((r) => {
        const cat = S.CAT_MAP[r.catId] || S.CAT_MAP.other;
        return {
          id: r.id,
          catName: cat.name,
          emoji: cat.emoji,
          color: cat.color,
          amountText: S.yuan(r.amount),
          note: r.note
        };
      })
    }));

    this.setData({
      curLabel: `${y} 年 ${m} 月`,
      isFuture,
      monthTotalText: S.yuan(sum.total),
      monthCount: sum.count,
      groups
    });
  },

  /* ---------- 长按删除（带确认） ---------- */
  onDelete(e) {
    const id = e.currentTarget.dataset.id;
    if (!id) return;

    wx.showModal({
      title: '删除这条记录？',
      content: '删除后无法恢复',
      confirmText: '删除',
      confirmColor: '#e5484d',
      success: (res) => {
        if (!res.confirm) return;
        S.deleteRecord(id);
        this.render();
        wx.showToast({ title: '已删除', icon: 'success' });
      }
    });
  }
});
