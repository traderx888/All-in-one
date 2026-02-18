// 基本測試：確認模組可以正確載入
const assert = require('assert');

// 測試 slack 模組可以載入
const slack = require('../src/slack');
assert.strictEqual(typeof slack.notifySlack, 'function', 'notifySlack should be a function');
assert.strictEqual(typeof slack.notifyError, 'function', 'notifyError should be a function');
assert.strictEqual(typeof slack.sendToSlack, 'function', 'sendToSlack should be a function');

// 測試 monitor 模組可以載入
const monitor = require('../src/monitor');
assert.strictEqual(typeof monitor.reportError, 'function', 'reportError should be a function');

// 測試沒有設定 SLACK_WEBHOOK_URL 時不會拋錯
(async () => {
  // 應該靜默跳過，不拋出例外
  await slack.notifySlack('test message');
  await slack.notifyError(new Error('test error'));
  await monitor.reportError(new Error('test reported error'));

  console.log('All tests passed');
})();
