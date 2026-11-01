const S = require('./utils/store.js');

App({
  globalData: { version: '1.0.0' },
  onLaunch() {
    // 首次启动初始化设置，避免各页面读空
    S.readSettings();
  }
});
