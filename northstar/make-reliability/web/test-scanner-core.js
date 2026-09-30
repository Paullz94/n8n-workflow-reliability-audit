const assert = require('node:assert/strict');
const fs = require('node:fs');
const scanner = require('./scanner-core.js');

function rules(bp) { return new Set(scanner.scanBlueprint(bp).map(f => f.rule)); }

assert.ok(rules({ flow: [{ id: 1, module: 'google-sheets:createRow', mapper: {} }] }).has('write-without-error-handler'));
assert.ok(rules({ flow: [{ id: 1, module: 'http:ActionSendData', mapper: { method: 'POST' } }] }).has('http-write-idempotency-review'));
assert.ok(rules({ blueprint: JSON.stringify({ flow: [{ id: 1, module: 'crm:updateContact', mapper: {} }] }) }).has('write-without-error-handler'));
assert.ok(rules({ flow: [{ id: 1, module: 'crm:updateContact', mapper: {}, onerror: [{ id: 2, module: 'builtin:Break', mapper: { retry: true } }] }] }).has('retrying-write-idempotency-review'));
const safety = rules({ flow: [{ id: 1, module: 'crm:updateContact', mapper: {} }], metadata: { instant: true, scenario: { sequential: false, dlq: false, dataloss: true, confidential: true } } });
for (const rule of ['concurrency-review','incomplete-executions-disabled-review','data-loss-enabled','confidential-observability-review']) assert.ok(safety.has(rule), rule);

assert.ok(rules({ flow: [{ id: 1, module: 'crm:updateContact', mapper: {}, onerror: [{ id: 2, module: 'builtin:Ignore', mapper: {} }] }] }).has('write-skip-handler-data-loss-review'));
assert.ok(rules({ flow: [{ id: 1, module: 'crm:updateContact', mapper: {}, onerror: [{ id: 2, module: 'builtin:Resume', mapper: {} }] }] }).has('write-resume-handler-silent-success-review'));
assert.ok(rules({ flow: [{ id: 1, module: 'crm:updateContact', mapper: {}, onerror: [{ id: 2, module: 'builtin:Commit', mapper: {} }] }] }).has('write-commit-partial-state-review'));
const rollback = rules({ flow: [{ id: 1, module: 'crm:updateContact', mapper: {}, onerror: [{ id: 2, module: 'builtin:Rollback', mapper: {} }] }], metadata: { scenario: { autoCommit: true, dlq: true } } });
assert.ok(rollback.has('auto-commit-recovery-review'));
assert.ok(rollback.has('rollback-limited-by-autocommit-review'));
const secret = scanner.scanBlueprint({ flow: [{ id: 1, module: 'http:ActionSendData', mapper: { token: 'Bearer abcdefghijklmnopqrstuvwxyz123456' } }] });
const secretFinding = secret.find(f => f.rule === 'possible-secret-in-blueprint');
assert.ok(secretFinding);
assert.ok(!secretFinding.message.includes('abcdefghijklmnopqrstuvwxyz'));
const makeHook = scanner.scanBlueprint({ flow: [{ id: 1, module: 'http:ActionSendData', mapper: { url: 'https://hook.eu1.make.com/abcdefghijklmnopqrstuvwxyz123456' } }] });
assert.ok(makeHook.some(f => f.rule === 'possible-secret-in-blueprint'));
for (const providerSecret of [
  'sk_' + 'live_' + '1234567890abcdefghijklmnop',
  'ghp_' + '1234567890abcdefghijklmnopqrst',
  'AKIA' + '1234567890ABCDEF',
  'AIza' + '1234567890abcdefghijklmnopqrstuvw',
  'xoxb-' + '1234567890-' + 'abcdefghijklmno'
]) {
  const hits = scanner.scanBlueprint({ flow: [{ id: 1, module: 'http:ActionSendData', mapper: { value: providerSecret } }] });
  assert.ok(hits.some(f => f.rule === 'possible-secret-in-blueprint'), providerSecret.slice(0, 8));
}

const index = fs.readFileSync('./index.html', 'utf8');
assert.ok(index.includes('Local-only core scan'));
assert.ok(!/https?:\/\/[^"'\s<]+\.js\b/i.test(index), 'No remote JS dependency expected');
assert.ok(!/\b(fetch|XMLHttpRequest|WebSocket)\s*\(/.test(index), 'Core UI must not perform network calls');
console.log('scanner-core browser tests: PASS');
