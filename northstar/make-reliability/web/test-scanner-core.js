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
const secret = scanner.scanBlueprint({ flow: [{ id: 1, module: 'http:ActionSendData', mapper: { token: 'Bearer abcdefghijklmnopqrstuvwxyz123456' } }] });
const secretFinding = secret.find(f => f.rule === 'possible-secret-in-blueprint');
assert.ok(secretFinding);
assert.ok(!secretFinding.message.includes('abcdefghijklmnopqrstuvwxyz'));

const index = fs.readFileSync('./index.html', 'utf8');
assert.ok(index.includes('Local-only core scan'));
assert.ok(!/https?:\/\/[^"'\s<]+\.js\b/i.test(index), 'No remote JS dependency expected');
assert.ok(!/\b(fetch|XMLHttpRequest|WebSocket)\s*\(/.test(index), 'Core UI must not perform network calls');
console.log('scanner-core browser tests: PASS');
