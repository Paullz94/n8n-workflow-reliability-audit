(() => {
  'use strict';

  function readPath(obj, path) {
    return path.split('.').reduce((v, k) => v && typeof v === 'object' ? v[k] : undefined, obj);
  }

  function analyzeWorkflow(wf) {
    const workflow = wf && typeof wf === 'object' ? wf : {};
    const nodes = Array.isArray(workflow.nodes) ? workflow.nodes : [];
    const findings = [];
    const names = new Map();

    for (const n of nodes) {
      const name = n && n.name ? String(n.name) : '(unnamed node)';
      names.set(name, (names.get(name) || 0) + 1);
    }

    const dupes = [...names.entries()].filter(([, count]) => count > 1).map(([name]) => name);
    if (dupes.length) {
      findings.push({
        severity: 'high',
        title: 'Duplicate node names',
        detail: `Duplicate names can make review and connection reasoning ambiguous: ${dupes.join(', ')}`
      });
    }

    const webhooks = nodes.filter(n => String((n && n.type) || '').toLowerCase().includes('webhook'));
    for (const n of webhooks) {
      const auth = n.parameters && n.parameters.authentication;
      if (!auth || String(auth).toLowerCase() === 'none') {
        findings.push({
          severity: 'high',
          title: 'Webhook may be unauthenticated',
          detail: `Node "${n.name || '(unnamed)'}" has no explicit webhook authentication in the export.`
        });
      }
    }

    const http = nodes.filter(n => String((n && n.type) || '').toLowerCase().includes('httprequest'));
    for (const n of http) {
      const timeout = readPath(n, 'parameters.options.timeout');
      if (timeout === undefined || timeout === null || timeout === '') {
        findings.push({
          severity: 'medium',
          title: 'HTTP timeout not obvious',
          detail: `Node "${n.name || '(unnamed)'}" has no explicit timeout visible at parameters.options.timeout.`
        });
      }
      if (!n.retryOnFail) {
        findings.push({
          severity: 'medium',
          title: 'HTTP retry posture needs review',
          detail: `Node "${n.name || '(unnamed)'}" does not have retryOnFail enabled at node level.`
        });
      }
    }

    const active = workflow.active === true;
    const errorWorkflow = readPath(workflow, 'settings.errorWorkflow');
    if (active && !errorWorkflow) {
      findings.push({
        severity: 'high',
        title: 'Active workflow without an error workflow',
        detail: 'The export is active but settings.errorWorkflow is not configured.'
      });
    }

    const disabled = nodes.filter(n => n && n.disabled === true);
    if (disabled.length) {
      findings.push({
        severity: 'info',
        title: 'Disabled nodes present',
        detail: `${disabled.length} disabled node(s): ${disabled.map(n => n.name || '(unnamed)').join(', ')}`
      });
    }

    const powerful = nodes.filter(n => /code|function|executecommand|ssh/i.test(String((n && n.type) || '')));
    if (powerful.length) {
      findings.push({
        severity: 'info',
        title: 'Powerful execution nodes deserve manual review',
        detail: `${powerful.length} code/command-style node(s) detected.`
      });
    }

    const sideEffectPattern = /stripe|gmail|slack|postgres|mysql|microsoftsql|googlesheets|hubspot|salesforce|sendemail|httprequest/i;
    const sideEffects = nodes.filter(n => sideEffectPattern.test(String((n && n.type) || '')));
    const likelyNoRetryGuard = sideEffects.filter(
      n => !n.retryOnFail && !/read|get|search|list/i.test(String(n.name || ''))
    );
    if (likelyNoRetryGuard.length >= 3) {
      findings.push({
        severity: 'medium',
        title: 'Multiple side-effect nodes need recovery review',
        detail: `${likelyNoRetryGuard.length} write-capable/integration nodes appear without node-level retry enabled. This is only a heuristic and requires manual validation.`
      });
    }

    if (!nodes.length) {
      findings.push({
        severity: 'high',
        title: 'No nodes found',
        detail: 'This does not look like a normal n8n workflow export.'
      });
    }

    if (!findings.length) {
      findings.push({
        severity: 'ok',
        title: 'No quick-scan flags',
        detail: 'The lightweight browser checks found no obvious flags. This does not prove production reliability.'
      });
    }

    return {
      generated_at: new Date().toISOString(),
      workflow_name: workflow.name || '(unnamed)',
      node_count: nodes.length,
      active,
      counts: {
        webhook_nodes: webhooks.length,
        http_request_nodes: http.length,
        disabled_nodes: disabled.length,
        powerful_nodes: powerful.length
      },
      findings
    };
  }

  function escapeHtml(value) {
    return String(value).replace(/[&<>"']/g, c => ({
      '&': '&amp;',
      '<': '&lt;',
      '>': '&gt;',
      '"': '&quot;',
      "'": '&#39;'
    }[c]));
  }

  function bindBrowserUi() {
    if (typeof document === 'undefined') return;

    const file = document.getElementById('file');
    const scanBtn = document.getElementById('scanBtn');
    const downloadBtn = document.getElementById('downloadBtn');
    const results = document.getElementById('results');
    const fileMeta = document.getElementById('fileMeta');
    if (!file || !scanBtn || !downloadBtn || !results || !fileMeta) return;

    let lastReport = null;

    file.addEventListener('change', () => {
      const f = file.files && file.files[0];
      fileMeta.textContent = f
        ? `${f.name} · ${Math.round(f.size / 1024)} KB · processed locally`
        : 'Nothing selected.';
    });

    function render(report) {
      const summary = `<div class="metric"><span>Workflow</span><strong>${escapeHtml(report.workflow_name)}</strong></div>
        <div class="metric"><span>Nodes</span><strong>${report.node_count}</strong></div>
        <div class="metric"><span>Quick-scan findings</span><strong>${report.findings.length}</strong></div>`;
      const rows = report.findings.map(f =>
        `<div class="finding"><span class="sev ${escapeHtml(f.severity)}">${escapeHtml(f.severity.toUpperCase())}</span><strong>${escapeHtml(f.title)}</strong><div class="small" style="margin-top:5px">${escapeHtml(f.detail)}</div></div>`
      ).join('');
      results.innerHTML = summary + rows +
        '<p class="small">This quick scan is heuristic. Use the public Python analyzer or a fixed-scope audit for deeper review.</p>';
    }

    scanBtn.addEventListener('click', async () => {
      const f = file.files && file.files[0];
      if (!f) {
        results.innerHTML = '<div class="finding"><span class="sev high">INPUT</span><strong>Select a JSON export first.</strong></div>';
        return;
      }
      try {
        const text = await f.text();
        const data = JSON.parse(text);
        const wf = Array.isArray(data) ? data[0] : data;
        lastReport = analyzeWorkflow(wf || {});
        render(lastReport);
        downloadBtn.disabled = false;
      } catch (e) {
        lastReport = null;
        downloadBtn.disabled = true;
        results.innerHTML = '<div class="finding"><span class="sev high">ERROR</span><strong>Could not parse this file as JSON.</strong><div class="small">Use a normal n8n workflow JSON export.</div></div>';
      }
    });

    downloadBtn.addEventListener('click', () => {
      if (!lastReport) return;
      const blob = new Blob([JSON.stringify(lastReport, null, 2)], { type: 'application/json' });
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = 'pcflows-quick-scan.json';
      a.click();
      setTimeout(() => URL.revokeObjectURL(url), 500);
    });
  }

  if (typeof module !== 'undefined' && module.exports) {
    module.exports = { analyzeWorkflow };
  }

  if (typeof window !== 'undefined') {
    bindBrowserUi();
  }
})();