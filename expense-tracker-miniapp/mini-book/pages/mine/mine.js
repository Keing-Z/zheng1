const S = require('../../utils/store.js');

Page({
  data: {
    streakDays: 0,
    todayDone: false,
    budgetDraft: '',
    budgetText: '未设置',
    budgetYuan: '0',
    spentText: '0',
    remainText: '0',
    overText: '0',
    barWidth: 0,
    budget: { level: 'none', pct: 0 },
    achList: [],
    unlockedCount: 0,
    totalRecords: 0
  },

  onShow() {
    this.refresh();
  },

  refresh() {
    const records = S.readRecords();
    const now = new Date();
    const settings = S.readSettings();
    const sum = S.summaryMonth(records, now.getFullYear(), now.getMonth() + 1);
    const budget = S.budgetStatus(settings.budget, sum.total);
    const st = S.streak(records, now);
    const achList = S.achievements(records);

    this.setData({
      streakDays: st.days,
      todayDone: st.todayDone,
      budgetDraft: settings.budget > 0 ? String(settings.budget / 100) : '',
      budgetYuan: S.yuan(budget.budget),
      budgetText: settings.budget > 0 ? `¥${S.yuan(settings.budget)} / 月` : '未设置',
      spentText: S.yuan(sum.total),
      remainText: S.yuan(Math.max(0, budget.remain)),
      overText: S.yuan(Math.abs(budget.remain)),
      barWidth: budget.level === 'none' ? 0 : Math.min(100, budget.pct),
      budget,
      achList,
      unlockedCount: achList.filter((x) => x.unlocked).length,
      totalRecords: records.length
    });
  },

  onBudgetInput(e) {
    this.setData({ budgetDraft: e.detail.value });
  },

  onSaveBudget() {
    const v = parseFloat(this.data.budgetDraft);
    if (this.data.budgetDraft !== '' && (isNaN(v) || v < 0)) {
      wx.showToast({ title: '请输入正确的金额', icon: 'none' });
      return;
    }
    const settings = S.readSettings();
    settings.budget = v > 0 ? Math.round(v * 100) : 0;
    S.writeSettings(settings);
    wx.showToast({ title: v > 0 ? '预算已设置' : '已清除预算', icon: 'success' });
    this.refresh();
  },

  /* 导出：把 JSON 写进剪贴板（小程序不给文件系统自由写权限，剪贴板最通用）
   * 注意：剪贴板属于微信的隐私接口，调用前先向用户说明，符合隐私规范。 */
  onExport() {
    const records = S.readRecords();
    if (!records.length) {
      wx.showToast({ title: '还没有数据', icon: 'none' });
      return;
    }

    wx.showModal({
      title: '导出备份',
      content: `将把本机的 ${records.length} 条记账记录以文本形式复制到剪贴板，方便你粘贴到备忘录保存。小程序不会读取剪贴板中的其他内容。`,
      confirmText: '复制',
      success: (res) => {
        if (!res.confirm) return;
        const payload = JSON.stringify({ v: 1, exportedAt: Date.now(), records });
        wx.setClipboardData({
          data: payload,
          success: () => {
            wx.showModal({
              title: '备份已复制',
              content: '已复制到剪贴板。建议立刻粘贴到微信收藏或备忘录里保存，避免数据丢失。',
              showCancel: false
            });
          },
          fail: () => wx.showToast({ title: '复制失败', icon: 'none' })
        });
      }
    });
  },

  /* 从剪贴板恢复：读取备份文本 → 校验 → 按 id 去重合并 */
  onHowToImport() {
    wx.getClipboardData({
      success: (res) => {
        const parsed = S.parseBackup(res.data);
        if (!parsed.ok) {
          wx.showModal({
            title: '没有读到有效备份',
            content: `${parsed.reason}。\n\n请先复制之前导出的备份文本，再来点击「从备份恢复」。`,
            showCancel: false
          });
          return;
        }
        wx.showModal({
          title: '发现备份',
          content: `读到 ${parsed.records.length} 条记录。导入时会与现有记录合并（重复的不会重复添加），是否继续？`,
          confirmText: '导入',
          success: (r) => {
            if (!r.confirm) return;
            const merged = S.mergeRecords(parsed.records);
            this.refresh();
            wx.showModal({
              title: '恢复完成',
              content: `新增 ${merged.added} 条，跳过重复 ${merged.skipped} 条。当前共 ${merged.total} 条记录。`,
              showCancel: false
            });
          }
        });
      },
      fail: () => {
        wx.showModal({
          title: '无法读取剪贴板',
          content: '请先复制备份文本后再试，或检查是否允许小程序访问剪贴板。',
          showCancel: false
        });
      }
    });
  }
});
