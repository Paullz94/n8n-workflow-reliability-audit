const test = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const { analyzeWorkflow } = require('../scanner.js');

function fixture(name) {
  return JSON.parse(fs.readFileSync(path.join(__dirname, '..', 'examples', name), 'utf8'));
}

test('unsafe order fixture surfaces core analyzer-class warnings', () => {
  const report = analyzeWorkflow(fixture('unsafe_order_intake.json'));
  const titles = new Set(report.findings.map(f => f.title));

  assert.equal(report.workflow_name, 'Unsafe Order Intake Demo');
  assert.equal(report.node_count, 4);
  assert.equal(report.active, true);
  assert.ok(titles.has('Webhook may be unauthenticated'));
  assert.ok(titles.has('HTTP timeout not obvious'));
  assert.ok(titles.has('HTTP retry posture needs review'));
  assert.ok(titles.has('Active workflow without an error workflow'));
  assert.ok(titles.has('Powerful execution node deserves manual review'));
  assert.ok(titles.has('Possible hard-coded secret'));
  assert.ok(titles.has('No visible duplicate-prevention step'));
  assert.ok(titles.has('No exported version identifier'));
});

test('hardened fixture has no browser quick-scan flags', () => {
  const report = analyzeWorkflow(fixture('hardened_order_intake.json'));
  assert.equal(report.findings.length, 1);
  assert.equal(report.findings[0].severity, 'ok');
  assert.equal(report.findings[0].title, 'No quick-scan flags');
});

test('duplicate and unreachable fixtures surface structure/graph issues', () => {
  const report = analyzeWorkflow(fixture('unsafe_duplicate_nodes.json'));
  const titles = new Set(report.findings.map(f => f.title));
  assert.ok(titles.has('Duplicate node names'));
});

test('malformed workflow shape fails closed with visible warnings', () => {
  const report = analyzeWorkflow({ name:'Empty' });
  const titles = new Set(report.findings.map(f => f.title));
  assert.ok(titles.has('Missing workflow identifier'));
  assert.ok(titles.has('No nodes found'));
});

test('scanner detects missing node identifiers', () => {
  const workflow = fixture('runtime_smoke.json');
  delete workflow.nodes[0].id;
  const report = analyzeWorkflow(workflow);
  assert.ok(report.findings.some(f => f.title === 'Nodes missing identifiers'));
});

test('continue-on-error is surfaced', () => {
  const workflow = fixture('runtime_smoke.json');
  workflow.nodes[0].continueOnFail = true;
  const report = analyzeWorkflow(workflow);
  assert.ok(report.findings.some(f => f.title === 'Node may convert a failure into success'));
});

test('scanner never echoes arbitrary credential values into findings', () => {
  const workflow = fixture('unsafe_order_intake.json');
  workflow.nodes[2].parameters.authorization = 'SUPER_SECRET_SHOULD_NOT_APPEAR';
  const report = analyzeWorkflow(workflow);
  const serialized = JSON.stringify(report);
  assert.equal(serialized.includes('SUPER_SECRET_SHOULD_NOT_APPEAR'), false);
  assert.ok(report.findings.some(f => f.title === 'Possible hard-coded secret'));
});
