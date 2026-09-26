const test = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const { analyzeWorkflow } = require('../scanner.js');

function fixture(name) {
  return JSON.parse(fs.readFileSync(path.join(__dirname, '..', 'examples', name), 'utf8'));
}

test('unsafe order fixture surfaces core reliability warnings', () => {
  const report = analyzeWorkflow(fixture('unsafe_order_intake.json'));
  const titles = new Set(report.findings.map(f => f.title));

  assert.equal(report.workflow_name, 'Unsafe Order Intake Demo');
  assert.equal(report.node_count, 4);
  assert.equal(report.active, true);
  assert.ok(titles.has('Webhook may be unauthenticated'));
  assert.ok(titles.has('HTTP timeout not obvious'));
  assert.ok(titles.has('HTTP retry posture needs review'));
  assert.ok(titles.has('Active workflow without an error workflow'));
  assert.ok(titles.has('Powerful execution nodes deserve manual review'));
});

test('malformed workflow shape fails closed with a visible warning', () => {
  const report = analyzeWorkflow({ name: 'Empty' });
  assert.equal(report.node_count, 0);
  assert.ok(report.findings.some(f => f.title === 'No nodes found' && f.severity === 'high'));
});

test('scanner never echoes arbitrary parameter values into findings', () => {
  const workflow = fixture('unsafe_order_intake.json');
  workflow.nodes[2].parameters.authorization = 'SUPER_SECRET_SHOULD_NOT_APPEAR';
  const report = analyzeWorkflow(workflow);
  const serialized = JSON.stringify(report);
  assert.equal(serialized.includes('SUPER_SECRET_SHOULD_NOT_APPEAR'), false);
});
