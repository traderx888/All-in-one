// Error 監控腳本
// 在專案進入點最上方 require 這個檔案即可啟用全局錯誤監控
// require('./monitor');

const { notifyError } = require('./slack');

let initialized = false;

/**
 * 初始化全域錯誤監控
 * 攔截 uncaughtException、unhandledRejection，自動發送到 Slack
 */
function initMonitor() {
  if (initialized) return;
  initialized = true;

  // 攔截未捕獲的同步例外
  process.on('uncaughtException', async (error) => {
    console.error('[monitor] Uncaught Exception:', error);
    try {
      await notifyError(error, { type: 'uncaughtException' });
    } catch (slackErr) {
      console.error('[monitor] Failed to notify Slack:', slackErr.message);
    }
    // uncaughtException 後應該退出，因為 process 狀態可能已經不一致
    process.exit(1);
  });

  // 攔截未處理的 Promise rejection
  process.on('unhandledRejection', async (reason) => {
    const error = reason instanceof Error ? reason : new Error(String(reason));
    console.error('[monitor] Unhandled Rejection:', error);
    try {
      await notifyError(error, { type: 'unhandledRejection' });
    } catch (slackErr) {
      console.error('[monitor] Failed to notify Slack:', slackErr.message);
    }
  });

  // 攔截 process warning（可選）
  process.on('warning', async (warning) => {
    console.warn('[monitor] Warning:', warning.message);
  });

  console.log('[monitor] Error monitoring initialized');
}

/**
 * 手動回報錯誤到 Slack（不會讓 process 退出）
 * 適合在 try/catch 區塊中使用
 *
 * @param {Error} error
 * @param {object} [context] - 額外上下文，例如 { userId, endpoint, requestBody }
 */
async function reportError(error, context = {}) {
  console.error('[monitor] Reported Error:', error);
  try {
    await notifyError(error, { type: 'reported', ...context });
  } catch (slackErr) {
    console.error('[monitor] Failed to notify Slack:', slackErr.message);
  }
}

// 自動初始化
initMonitor();

module.exports = { reportError };
