(() => {
  'use strict';

  const SECRET_KEY = /(api[_-]?key|password|passwd|secret|authorization|bearer|token)/i;
  const SECRET_VALUE = /(bearer\s+[a-z0-9._-]{12,}|sk-[a-z0-9_-]{12,})/i;
  const TRIGGER_MARKERS = ['trigger', 'webhook'];
  const RISKY_NODE_MARKERS = ['executecommand', 'readwritefile', 'ssh', 'code'];
  const SIDE_EFFECT_MARKERS = ['airtable','googlesheets','postgres','mysql','microsoftsql','slack','gmail','sendemail','httprequest'];
  const IDEMPOTENCY_MARKERS = ['dedup', 'idempoten', 'duplicate', 'already processed'];

  function readPath(obj, path) {
    return path.split('.').reduce((v, k) => v && typeof v === 'object' ? v[k] : undefined, obj);
  }

  function iterParamValues(value, path = 'parameters', out = []) {
    if (value && typeof value === 'object' && !Array.isArray(value)) {
      for (const [key, child] of Object.entries(value)) {
        const childPath = path + '.' + key;
        out.push({ path: childPath, key, value: child });
        iterParamValues(child, childPath, out);
      }
    } else if (Array.isArray(value)) {
      value.forEach((child, index) => iterParamValues(child, path + '[' + index + ']', out));
    }
    return out;
  }

  function nodeType(node) {
    return String((node && node.type) || '').toLowerCase();
  }

  function isTrigger(node) {
    const type = nodeType(node);
    return TRIGGER_MARKERS.some(marker => type.includes(marker));
  }

  function connectionTargets(connections) {
    const adjacency = new Map();
    if (!connections || typeof connections !== 'object') return adjacency;

    for (const [source, outputs] of Object.entries(connections)) {
      if (!outputs || typeof outputs !== 'object') continue;
      if (!adjacency.has(source)) adjacency.set(source, new Set());

      for (const channelGroups of Object.values(outputs)) {
        if (!Array.isArray(channelGroups)) continue;
        for (const group of channelGroups) {
          if (!Array.isArray(group)) continue;
          for (const edge of group) {
            if (edge && typeof edge.node === 'string') adjacency.get(source).add(edge.node);
          }
        }
      }
    }
    return adjacency;
  }

  function reachable(adjacency, roots) {
    const seen = new Set();
    const queue = [...roots];
    while (queue.length) {
      const current = queue.shift();
      if (seen.has(current)) continue;
      seen.add(current);
      const next = adjacency.get(current);
      if (next) {
        for (const target of next) if (!seen.has(target)) queue.push(target);
      }
    }
    return seen;
  }

  function add(findings, severity, title, detail, node = null, ruleId = null) {
    findings.push({ severity, title, detail, node, rule_id: ruleId });
  }

  function analyzeWorkflow(wf) {
    const workflow = wf && typeof wf === 'object' && !Array.isArray(wf) ? wf : {};
    const rawNodes = Array.isArray(workflow.nodes) ? workflow.nodes : [];
    const nodes = rawNodes.filter(n => n && typeof n === 'object');
    const findings = [];

    if (typeof workflow.id !== 'string' || !workflow.id.trim()) {
      add(findings, 'critical', 'Missing workflow identifier',
        'The export has no non-empty workflow id.', null, 'STRUCT-004');
    }

    const names = nodes.map(n => String(n.name || '').trim());
    const counts = new Map();
    for (const name of names) if (name) counts.set(name, (counts.get(name) || 0) + 1);

    const duplicates = [...counts.entries()].filter(([, count]) => count > 1).map(([name]) => name);
    if (duplicates.length) {
      add(findings, 'high', 'Duplicate node names',
        'Duplicate names can make expressions, connections, and incident reports ambiguous: ' + duplicates.join(', '),
        null, 'STRUCT-002');
    }

    const unnamed = names.filter(name => !name).length;
    if (unnamed) {
      add(findings, 'high', 'Unnamed nodes',
        unnamed + ' node(s) have no usable name.', null, 'STRUCT-003');
    }

    const missingNodeIds = nodes.filter(n => typeof n.id !== 'string' || !n.id.trim());
    if (missingNodeIds.length) {
      add(findings, 'high', 'Nodes missing identifiers',
        missingNodeIds.length + ' node(s) have no stable id.', null, 'STRUCT-005');
    }

    const adjacency = connectionTargets(workflow.connections || {});
    const incoming = new Map(names.filter(Boolean).map(name => [name, 0]));
    for (const targets of adjacency.values()) {
      for (const target of targets) incoming.set(target, (incoming.get(target) || 0) + 1);
    }

    let roots = new Set(nodes.filter(isTrigger).map(n => String(n.name || '')).filter(Boolean));
    if (!roots.size) roots = new Set([...incoming.entries()].filter(([, count]) => count === 0).map(([name]) => name));

    const seen = reachable(adjacency, roots);
    const disconnected = [...incoming.keys()].filter(name => !seen.has(name)).sort();
    if (disconnected.length) {
      add(findings, 'high', 'Unreachable nodes',
        'Not reachable from a trigger/root: ' + disconnected.join(', '), null, 'GRAPH-001');
    }

    const active = workflow.active === true;
    const errorWorkflow = readPath(workflow, 'settings.errorWorkflow');
    if (active && !errorWorkflow) {
      add(findings, 'high', 'Active workflow without an error workflow',
        'The export is active but settings.errorWorkflow is not configured.', null, 'RECOVERY-001');
    }

    let hasSideEffect = false;
    let hasIdempotencySignal = false;
    let webhookCount = 0;
    let httpCount = 0;
    let disabledCount = 0;
    let powerfulCount = 0;

    for (const node of nodes) {
      const name = String(node.name || '') || '(unnamed)';
      const type = nodeType(node);
      const params = node.parameters && typeof node.parameters === 'object' ? node.parameters : {};
      const identity = (name + ' ' + type).toLowerCase();

      if (IDEMPOTENCY_MARKERS.some(marker => identity.includes(marker))) hasIdempotencySignal = true;
      if (SIDE_EFFECT_MARKERS.some(marker => type.includes(marker))) hasSideEffect = true;

      if (type.includes('webhook')) {
        webhookCount += 1;
        const authentication = String(params.authentication || 'none').toLowerCase();
        if (!authentication || authentication === 'none') {
          add(findings, 'high', 'Webhook may be unauthenticated',
            'Webhook authentication is absent or set to none.', name, 'SEC-001');
        }
      }

      if (type.includes('httprequest')) {
        httpCount += 1;
        const timeout = readPath(node, 'parameters.options.timeout');
        if (!node.retryOnFail) {
          add(findings, 'medium', 'HTTP retry posture needs review',
            'retryOnFail is not enabled at node level.', name, 'RECOVERY-002');
        }
        if (timeout === undefined || timeout === null || timeout === '') {
          add(findings, 'medium', 'HTTP timeout not obvious',
            'No explicit parameters.options.timeout value is visible.', name, 'RECOVERY-003');
        }
      }

      const onError = String(node.onError || 'stopWorkflow');
      if (node.continueOnFail === true || !['', 'stopWorkflow'].includes(onError)) {
        add(findings, 'medium', 'Node may convert a failure into success',
          'The node continues after an error; verify the continuation path surfaces business failure.',
          name, 'RECOVERY-004');
      }

      if (node.disabled === true) {
        disabledCount += 1;
        add(findings, 'medium', 'Disabled node remains in workflow graph',
          'This node has disabled=true; confirm it is intentional or remove stale graph content.',
          name, 'OPS-002');
      }

      if (RISKY_NODE_MARKERS.some(marker => type.includes(marker))) {
        powerfulCount += 1;
        add(findings, 'medium', 'Powerful execution node deserves manual review',
          'Code, command, SSH, or file-operation nodes need explicit input and permission review.',
          name, 'SEC-002');
      }

      for (const item of iterParamValues(params)) {
        if (typeof item.value === 'string' && item.value.startsWith('={{')) continue;
        const keySuspicious = SECRET_KEY.test(item.key);
        const valueSuspicious = typeof item.value === 'string' && SECRET_VALUE.test(item.value);
        if ((keySuspicious && ![null, undefined, '', '={{...}}'].includes(item.value)) || valueSuspicious) {
          add(findings, 'critical', 'Possible hard-coded secret',
            'A credential-like value is present at ' + item.path + ' (value redacted).',
            name, 'SEC-003');
        }
      }
    }

    if (active && roots.size && hasSideEffect && !hasIdempotencySignal) {
      add(findings, 'high', 'No visible duplicate-prevention step',
        'An active trigger reaches side-effect-capable nodes, but no node name/type signals deduplication or idempotency. Human confirmation is required.',
        null, 'DATA-001');
    }

    if (active && !workflow.versionId) {
      add(findings, 'low', 'No exported version identifier',
        'The active workflow has no versionId in this export.', null, 'OPS-001');
    }

    if (!nodes.length) {
      add(findings, 'high', 'No nodes found',
        'This does not look like a normal n8n workflow export.', null, 'STRUCT-001');
    }

    const severityOrder = { critical:0, high:1, medium:2, low:3, info:4, ok:5 };
    findings.sort((a, b) =>
      (severityOrder[a.severity] ?? 99) - (severityOrder[b.severity] ?? 99) ||
      String(a.rule_id || '').localeCompare(String(b.rule_id || '')) ||
      String(a.node || '').localeCompare(String(b.node || ''))
    );

    if (!findings.length) {
      add(findings, 'ok', 'No quick-scan flags',
        'The browser checks found no obvious flags. This does not prove production reliability.');
    }

    return {
      generated_at: new Date().toISOString(),
      workflow_name: workflow.name || '(unnamed)',
      node_count: nodes.length,
      active,
      counts: {
        webhook_nodes: webhookCount,
        http_request_nodes: httpCount,
        disabled_nodes: disabledCount,
        powerful_nodes: powerfulCount
      },
      findings
    };
  }

  function escapeHtml(value) {
    return String(value).replace(/[&<>"']/g, c => ({
      '&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'
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
        ? f.name + ' · ' + Math.round(f.size / 1024) + ' KB · processed locally'
        : 'Nothing selected.';
    });

    function render(report) {
      const summary =
        '<div class="metric"><span>Workflow</span><strong>' + escapeHtml(report.workflow_name) + '</strong></div>' +
        '<div class="metric"><span>Nodes</span><strong>' + report.node_count + '</strong></div>' +
        '<div class="metric"><span>Quick-scan findings</span><strong>' + report.findings.length + '</strong></div>';
      const rows = report.findings.map(f =>
        '<div class="finding"><span class="sev ' + escapeHtml(f.severity) + '">' +
        escapeHtml(f.severity.toUpperCase()) + '</span><strong>' +
        escapeHtml(f.title) + '</strong><div class="small" style="margin-top:5px">' +
        escapeHtml(f.detail) + '</div></div>'
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
      const blob = new Blob([JSON.stringify(lastReport, null, 2)], { type:'application/json' });
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = 'pcflows-quick-scan.json';
      a.click();
      setTimeout(() => URL.revokeObjectURL(url), 500);
    });
  }

  if (typeof module !== 'undefined' && module.exports) {
    module.exports = { analyzeWorkflow, connectionTargets, reachable };
  }

  if (typeof window !== 'undefined') bindBrowserUi();
})();