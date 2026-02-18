# CLAUDE.md

## Project Overview
Node.js application with Slack error monitoring integration. Zero external dependencies.

## Commands
- `npm start` - Start the server
- `npm test` - Run tests
- `npm run monitor` - Start monitor standalone

## Architecture
```
src/
  slack.js    - Slack webhook client (notifySlack, notifyError, sendToSlack)
  monitor.js  - Global error monitor (uncaughtException, unhandledRejection, reportError)
  index.js    - HTTP server entry point
```

## Key Patterns
- `require('./monitor')` at the top of any entry point enables global error capture
- `reportError(error, context)` for manual error reporting inside try/catch
- All Slack notifications are fire-and-forget with graceful fallback when webhook is not configured

## Environment Variables
- `SLACK_WEBHOOK_URL` - Required for Slack notifications
- `SLACK_CHANNEL` - Target channel (default: #error-alerts)
- `APP_NAME` - App name shown in alerts (default: All-in-one)

## Bug Fix Workflow
When investigating a bug reported via Slack:
1. Read the error message and stack trace from the Slack notification
2. Locate the relevant source file and line number from the stack trace
3. Run `npm test` to verify current state
4. Fix the bug
5. Run `npm test` to verify the fix
6. Commit and create a PR
