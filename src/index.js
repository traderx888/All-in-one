// 專案進入點
// monitor 必須在最上方 require，才能攔截所有錯誤
require('./monitor');

const http = require('http');
const { reportError } = require('./monitor');

const PORT = process.env.PORT || 3000;

const server = http.createServer(async (req, res) => {
  try {
    if (req.url === '/') {
      res.writeHead(200, { 'Content-Type': 'application/json' });
      res.end(JSON.stringify({ status: 'ok', app: 'All-in-one' }));
      return;
    }

    if (req.url === '/health') {
      res.writeHead(200, { 'Content-Type': 'application/json' });
      res.end(JSON.stringify({ status: 'healthy', uptime: process.uptime() }));
      return;
    }

    // 測試用：手動觸發一個錯誤發送到 Slack
    if (req.url === '/test-error') {
      const testError = new Error('This is a test error from /test-error endpoint');
      await reportError(testError, {
        endpoint: '/test-error',
        method: req.method,
      });
      res.writeHead(200, { 'Content-Type': 'application/json' });
      res.end(JSON.stringify({ status: 'error reported to slack' }));
      return;
    }

    res.writeHead(404, { 'Content-Type': 'application/json' });
    res.end(JSON.stringify({ error: 'Not Found' }));
  } catch (err) {
    await reportError(err, { endpoint: req.url, method: req.method });
    res.writeHead(500, { 'Content-Type': 'application/json' });
    res.end(JSON.stringify({ error: 'Internal Server Error' }));
  }
});

server.listen(PORT, () => {
  console.log(`[app] Server running on http://localhost:${PORT}`);
  console.log(`[app] Test error reporting: http://localhost:${PORT}/test-error`);
});
