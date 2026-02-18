// Slack Webhook 通知模組
// 用法: const { notifySlack, notifyError } = require('./slack');

const https = require('https');
const http = require('http');

const SLACK_WEBHOOK_URL = process.env.SLACK_WEBHOOK_URL;
const SLACK_CHANNEL = process.env.SLACK_CHANNEL || '#error-alerts';
const APP_NAME = process.env.APP_NAME || 'All-in-one';

/**
 * 發送訊息到 Slack webhook
 * @param {object} payload - Slack message payload
 * @returns {Promise<void>}
 */
function sendToSlack(payload) {
  return new Promise((resolve, reject) => {
    if (!SLACK_WEBHOOK_URL) {
      console.warn('[slack] SLACK_WEBHOOK_URL not set, skipping notification');
      return resolve();
    }

    const url = new URL(SLACK_WEBHOOK_URL);
    const transport = url.protocol === 'https:' ? https : http;
    const data = JSON.stringify(payload);

    const req = transport.request(
      {
        hostname: url.hostname,
        port: url.port,
        path: url.pathname,
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Content-Length': Buffer.byteLength(data),
        },
      },
      (res) => {
        if (res.statusCode === 200) {
          resolve();
        } else {
          reject(new Error(`Slack webhook returned ${res.statusCode}`));
        }
      }
    );

    req.on('error', reject);
    req.write(data);
    req.end();
  });
}

/**
 * 發送一般訊息到 Slack
 * @param {string} text - 訊息內容
 */
async function notifySlack(text) {
  await sendToSlack({ text, channel: SLACK_CHANNEL });
}

/**
 * 發送格式化的 error 通知到 Slack
 * 包含 stack trace、時間戳、環境資訊
 * @param {Error} error - Error 物件
 * @param {object} [context] - 額外的上下文資訊
 */
async function notifyError(error, context = {}) {
  const timestamp = new Date().toISOString();
  const env = process.env.NODE_ENV || 'development';

  const blocks = [
    {
      type: 'header',
      text: {
        type: 'plain_text',
        text: `🚨 Error in ${APP_NAME}`,
      },
    },
    {
      type: 'section',
      fields: [
        { type: 'mrkdwn', text: `*Environment:*\n${env}` },
        { type: 'mrkdwn', text: `*Time:*\n${timestamp}` },
      ],
    },
    {
      type: 'section',
      text: {
        type: 'mrkdwn',
        text: `*Error:*\n\`\`\`${error.message}\`\`\``,
      },
    },
  ];

  if (error.stack) {
    // 限制 stack trace 長度，Slack 有 3000 字元限制
    const stack = error.stack.length > 2500
      ? error.stack.substring(0, 2500) + '\n... (truncated)'
      : error.stack;

    blocks.push({
      type: 'section',
      text: {
        type: 'mrkdwn',
        text: `*Stack Trace:*\n\`\`\`${stack}\`\`\``,
      },
    });
  }

  if (Object.keys(context).length > 0) {
    const contextStr = JSON.stringify(context, null, 2);
    blocks.push({
      type: 'section',
      text: {
        type: 'mrkdwn',
        text: `*Context:*\n\`\`\`${contextStr}\`\`\``,
      },
    });
  }

  // 加一個提示：可以 tag Claude 來修 bug
  blocks.push({
    type: 'context',
    elements: [
      {
        type: 'mrkdwn',
        text: '💡 Tag `@Claude` and say "幫我調查修這個bug" to auto-fix',
      },
    ],
  });

  await sendToSlack({ channel: SLACK_CHANNEL, blocks });
}

module.exports = { notifySlack, notifyError, sendToSlack };
