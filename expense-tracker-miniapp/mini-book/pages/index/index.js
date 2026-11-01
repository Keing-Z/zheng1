const S = require('../../utils/store.js');

Page({
  data: {
    cats: S.CATS,
    catId: 'food',
    displayAmount: '0',
    note: '',
    monthTotalText: '0',
    todayCount: 0,
    streakDays: 0,
    budget: { level: 'none', pct: 0, remain: 0 },
    overText: '0',
    remainText: '0',
    barWidth: 0,
    savedTip: false
  },

  onLoad() {
    this.onShow();
  },

  onShow() {
    this.refresh();
  },

  refresh() {
    const records = S.readRecords();
    const now = new Date();
    const sum = S.summaryMonth(records, now.getFullYear(), now.getMonth() + 1);
    const todayKey = S.ymd(now);
    const todayCount = records.filter((r) => r.date === todayKey).length;
    const st = S.streak(records, now);
    const settings = S.readSettings();
    const budget = S.budgetStatus(settings.budget, sum.total);

    this.setData({
      monthTotalText: S.yuan(sum.total),
      todayCount,
      streakDays: st.days,
      budget,
      overText: S.yuan(Math.abs(budget.remain)),
      remainText: S.yuan(Math.max(0, budget.remain)),
      barWidth: budget.level === 'none' ? 0 : Math.min(100, budget.pct)
    });
  },

  /* ---------- 键盘输入 ---------- */
  onKey(e) {
    const k = e.currentTarget.dataset.k;
    let v = this.data.displayAmount;

    if (k === 'clear') v = '0';
    else if (k === 'del') {
      v = v.length <= 1 ? '0' : v.slice(0, -1);
      if (v === '') v = '0';
    } else if (k === '.') {
      if (v.indexOf('.') >= 0) return;
      v = v + '.';
    } else {
      // 数字
      if (v === '0') v = k;
      else {
        // 小数位最多 2 位
        const dot = v.indexOf('.');
        if (dot >= 0 && v.length - dot > 2) return;
        // 整数位最多 7 位
        if (dot < 0 && v.length >= 7) return;
        v = v + k;
      }
    }

    this.setData({ displayAmount: v });
  },

  onNoteInput(e) {
    this.setData({ note: e.detail.value });
  },

  onPickCat(e) {
    this.setData({ catId: e.currentTarget.dataset.id });
  },

  /* ---------- 保存 ---------- */
  onSave() {
    const raw = this.data.displayAmount;
    const amountYuan = parseFloat(raw);
    if (!amountYuan || amountYuan <= 0) {
      wx.showToast({ title: '请输入金额', icon: 'none' });
      return;
    }
    const amount = Math.round(amountYuan * 100); // 以分为单位，避免浮点误差

    S.addRecord({
      type: 'expense',
      amount,
      catId: this.data.catId,
      note: this.data.note.trim(),
      date: S.ymd(new Date())
    });

    wx.vibrateShort && wx.vibrateShort({ type: 'light' });

    // 记完立刻清空，方便连着记下一笔
    this.setData({ displayAmount: '0', note: '', savedTip: true });
    setTimeout(() => this.setData({ savedTip: false }), 1200);
    this.refresh();
  }
});
