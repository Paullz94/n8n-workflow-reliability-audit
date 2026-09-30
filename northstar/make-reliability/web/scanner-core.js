(function (root, factory) {
  const api = factory();
  if (typeof module !== 'undefined' && module.exports) module.exports = api;
  root.PCFlowsScanner = api;
})(typeof globalThis !== 'undefined' ? globalThis : this, function () {
  'use strict';

  const severityOrder = { info: 0, low: 1, medium: 2, high: 3, critical: 4 };
  const writeActions = [
    'create', 'update', 'delete', 'remove', 'send', 'post', 'put', 'patch',
    'upload', 'insert', 'add', 'write', 'set'
  ];
  const httpWriteMethods = new Set(['POST', 'PUT', 'PATCH', 'DELETE']);
  const secretPatterns = [
    /\bBearer\s+[A-Za-z0-9._~+/=-]{16,}/i,
    /\bsk-[A-Za-z0-9_-]{16,}\b/,
    /\b(?:sk|rk)_live_[A-Za-z0-9]{16,}\b/,
    /\bghp_[A-Za-z0-9]{20,}\b/,
    /\bgithub_pat_[A-Za-z0-9_]{20,}\b/,
    /\bAKIA[A-Z0-9]{16}\b/,
    /\bAIza[A-Za-z0-9_-]{30,}\b/,
    /\bxox[baprs]-[A-Za-z0-9-]{10,}\b/,
    /https:\/\/hooks\.slack\.com\/services\/[A-Za-z0-9/_-]+/i,
    /https:\/\/hook(?:\.[a-z0-9-]+)?\.make\.com\/[A-Za-z0-9_-]{12,}/i,
    /https:\/\/hook\.integromat\.com\/[A-Za-z0-9_-]{12,}/i,
    /(?:api[_-]?key|secret|token)\s*[:=]\s*[A-Za-z0-9._~+/=-]{12,}/i
  ];

  function normalizeBlueprint(doc) {
    if (!doc || typeof doc !== 'object' || Array.isArray(doc)) return doc;
    if (Array.isArray(doc.flow)) return doc;
    if (doc.blueprint && typeof doc.blueprint === 'object' && !Array.isArray(doc.blueprint)) return doc.blueprint;
    if (typeof doc.blueprint === 'string') {
      try {
        const parsed = JSON.parse(doc.blueprint);
        if (parsed && typeof parsed === 'object' && !Array.isArray(parsed)) return parsed;
      } catch (_) {}
    }
    if (Array.isArray(doc.subflows) && doc.subflows.length > 0) {
      const first = doc.subflows[0];
      if (first && Array.isArray(first.flow)) {
        return { name: doc.name || 'Module export', flow: first.flow, metadata: doc.metadata || {} };
      }
    }
    return doc;
  }

  function childFlows(module) {
    const out = [];
    for (const key of ['routes', 'onerror', 'branches']) {
      const value = module && module[key];
      if (!Array.isArray(value)) continue;
      value.forEach((item, index) => {
        if (!item || typeof item !== 'object') return;
        if (Array.isArray(item.flow)) out.push([`${key}[${index}].flow`, item.flow]);
        else if (item.module) out.push([`${key}[${index}]`, [item]]);
      });
    }
    return out;
  }

  function walkModules(flow, prefix = 'flow', out = []) {
    if (!Array.isArray(flow)) return out;
    flow.forEach((module, index) => {
      if (!module || typeof module !== 'object' || Array.isArray(module)) return;
      const path = `${prefix}[${index}]`;
      out.push([module, path]);
      childFlows(module).forEach(([name, nested]) => walkModules(nested, `${path}.${name}`, out));
    });
    return out;
  }

  function moduleName(module) {
    return String((module && module.module) || '');
  }

  function hasErrorHandler(module) {
    return Array.isArray(module && module.onerror) && module.onerror.length > 0;
  }

  function isTruthy(value) {
    if (value === true || value === 1) return true;
    return typeof value === 'string' && ['1', 'true', 'yes'].includes(value.trim().toLowerCase());
  }

  function isWriteModule(module) {
    const name = moduleName(module);
    const parts = name.split(':');
    const namespace = parts.length > 1 ? parts[0].toLowerCase() : '';
    if (['util', 'json', 'builtin', 'tools'].includes(namespace)) return false;
    const action = parts[parts.length - 1].toLowerCase();
    if (writeActions.some(word => action.startsWith(word) || action.startsWith(`action${word}`))) return true;
    if (name.toLowerCase().startsWith('http:')) {
      const mapper = module && typeof module.mapper === 'object' && module.mapper ? module.mapper : {};
      const method = String(mapper.method || module.method || '').toUpperCase();
      return httpWriteMethods.has(method);
    }
    return false;
  }

  function errorDirectives(module) {
    if (!Array.isArray(module && module.onerror)) return new Set();
    const directives = new Set();
    const stack = module.onerror.filter(x => x && typeof x === 'object' && !Array.isArray(x));
    while (stack.length) {
      const item = stack.pop();
      const name = moduleName(item).toLowerCase();
      if (name.startsWith('builtin:')) directives.add(name);
      if (Array.isArray(item.flow)) {
        item.flow.forEach(x => {
          if (x && typeof x === 'object' && !Array.isArray(x)) stack.push(x);
        });
      }
    }
    return directives;
  }

  function hasRetryHandler(module) {
    if (!Array.isArray(module && module.onerror)) return false;
    const stack = module.onerror.filter(x => x && typeof x === 'object' && !Array.isArray(x));
    while (stack.length) {
      const item = stack.pop();
      if (moduleName(item).toLowerCase() === 'builtin:break') {
        const mapper = item.mapper && typeof item.mapper === 'object' ? item.mapper : {};
        if (isTruthy(mapper.retry)) return true;
      }
      if (Array.isArray(item.flow)) {
        item.flow.forEach(x => {
          if (x && typeof x === 'object' && !Array.isArray(x)) stack.push(x);
        });
      }
    }
    return false;
  }

  function allStrings(value, out = []) {
    if (typeof value === 'string') out.push(value);
    else if (Array.isArray(value)) value.forEach(v => allStrings(v, out));
    else if (value && typeof value === 'object') Object.values(value).forEach(v => allStrings(v, out));
    return out;
  }

  function finding(rule, severity, message, module, path) {
    return {
      rule,
      severity,
      message,
      module_id: module && Object.prototype.hasOwnProperty.call(module, 'id') ? module.id : null,
      module: module ? moduleName(module) || null : null,
      path: path || null
    };
  }

  function scanBlueprint(input) {
    if (!input || typeof input !== 'object' || Array.isArray(input)) {
      return [finding('invalid-blueprint', 'critical', 'Blueprint root must be a JSON object.')];
    }
    const bp = normalizeBlueprint(input);
    if (!bp || !Array.isArray(bp.flow)) {
      return [finding('invalid-blueprint', 'critical', "Top-level 'flow' array is missing or invalid.")];
    }
    if (bp.flow.length === 0) {
      return [finding('empty-flow', 'high', 'Scenario contains no modules.')];
    }

    const modules = walkModules(bp.flow);
    const writes = modules.filter(([m]) => isWriteModule(m));
    const findings = [];

    modules.forEach(([module, path]) => {
      const name = moduleName(module);
      if (isWriteModule(module) && !hasErrorHandler(module)) {
        findings.push(finding(
          'write-without-error-handler', 'high',
          'Write-like module has no exported onerror route; verify failure handling and recovery behavior.',
          module, path
        ));
      }
      if (isWriteModule(module) && hasRetryHandler(module)) {
        findings.push(finding(
          'retrying-write-idempotency-review', 'medium',
          'Write-like module has an automatic retry handler. Verify a retry cannot duplicate or repeat an external side effect.',
          module, path
        ));
      }
      if (isWriteModule(module)) {
        const directives = errorDirectives(module);
        if (directives.has('builtin:ignore')) {
          findings.push(finding(
            'write-skip-handler-data-loss-review', 'high',
            "Write-like module uses Make's Skip/Ignore directive. A failed bundle can be dropped while the scenario continues and may still appear successful.",
            module, path
          ));
        }
        if (directives.has('builtin:resume')) {
          findings.push(finding(
            'write-resume-handler-silent-success-review', 'high',
            "Write-like module uses Make's Resume directive. The failed write can be replaced with substitute output while downstream processing continues.",
            module, path
          ));
        }
        if (directives.has('builtin:commit')) {
          findings.push(finding(
            'write-commit-partial-state-review', 'medium',
            "Write-like module uses Make's Commit directive. Earlier transactional changes can be preserved while the current run stops, creating intentional partial state.",
            module, path
          ));
        }
      }
      if (name.toLowerCase().startsWith('http:')) {
        const mapper = module.mapper && typeof module.mapper === 'object' ? module.mapper : {};
        const method = String(mapper.method || module.method || '').toUpperCase();
        if (httpWriteMethods.has(method)) {
          findings.push(finding(
            'http-write-idempotency-review', 'medium',
            `HTTP ${method} can mutate external state; verify duplicate protection/idempotency before retries.`,
            module, path
          ));
        }
      }
      if (module.filter && isWriteModule(module)) {
        findings.push(finding(
          'filtered-write-silent-skip-review', 'medium',
          'A filter gates a write-like module. Verify that a non-match cannot produce a business-level silent success.',
          module, path
        ));
      }
      const designer = module.metadata && module.metadata.designer;
      const messages = designer && Array.isArray(designer.messages) ? designer.messages : [];
      messages.forEach(msg => {
        if (!msg || typeof msg !== 'object') return;
        const level = String(msg.severity || '').toLowerCase();
        if (!['warning', 'error'].includes(level)) return;
        findings.push(finding(
          'exported-designer-message', level === 'error' ? 'high' : 'medium',
          `Make exported a ${msg.severity} for this module: ${msg.message || 'no message'}`,
          module, path
        ));
      });
    });

    const metadata = bp.metadata && typeof bp.metadata === 'object' ? bp.metadata : {};
    const scenario = metadata.scenario && typeof metadata.scenario === 'object' ? metadata.scenario : {};
    const instant = metadata.instant === true;

    if (writes.length && scenario.sequential === false) {
      findings.push(finding(
        'concurrency-review', instant ? 'medium' : 'low',
        'Scenario allows overlapping runs and contains write-like modules. Verify concurrent executions cannot race or duplicate writes.'
      ));
    }
    if (writes.length && scenario.autoCommit === true) {
      findings.push(finding(
        'auto-commit-recovery-review', 'low',
        'Scenario has autoCommit=true and performs writes. For transaction-capable modules, earlier committed changes may no longer be reversible after a later failure.'
      ));
    }
    const rollbackPaths = modules
      .filter(([m]) => errorDirectives(m).has('builtin:rollback'))
      .map(([, p]) => p);
    if (rollbackPaths.length && scenario.autoCommit === true) {
      const f = finding(
        'rollback-limited-by-autocommit-review', 'medium',
        'Rollback handler is present while autoCommit=true. Previously committed transactional changes cannot be rolled back by a later error.'
      );
      f.path = rollbackPaths[0];
      findings.push(f);
    }
    if (writes.length && scenario.dlq === false) {
      findings.push(finding(
        'incomplete-executions-disabled-review', 'medium',
        'Exported scenario has dlq=false. Verify that disabling stored incomplete executions is intentional for a workflow with external writes.'
      ));
    }
    if (scenario.dataloss === true) {
      findings.push(finding(
        'data-loss-enabled', 'high',
        'Scenario is exported with data-loss mode enabled; failed data may be discarded when incomplete-execution storage cannot accept more items.'
      ));
    }
    if (scenario.confidential === true) {
      findings.push(finding(
        'confidential-observability-review', 'low',
        'Keep-data-confidential is enabled. Verify external observability exists because Make execution logs retain less payload detail.'
      ));
    }

    const possibleSecret = allStrings(bp).some(text => secretPatterns.some(pattern => pattern.test(text)));
    if (possibleSecret) {
      findings.push(finding(
        'possible-secret-in-blueprint', 'critical',
        'Possible credential or secret-like literal detected. Sanitize the blueprint before sharing or storing it.'
      ));
    }

    return findings.sort((a, b) => {
      const severity = severityOrder[b.severity] - severityOrder[a.severity];
      if (severity) return severity;
      return `${a.rule}:${a.path || ''}`.localeCompare(`${b.rule}:${b.path || ''}`);
    });
  }

  function summarize(findings) {
    const counts = { critical: 0, high: 0, medium: 0, low: 0, info: 0 };
    findings.forEach(f => { if (Object.prototype.hasOwnProperty.call(counts, f.severity)) counts[f.severity] += 1; });
    return counts;
  }

  function renderMarkdown(source, findings) {
    const counts = summarize(findings);
    const lines = [
      '# Make Scenario Reliability Preflight', '',
      `Source: \`${source || 'local blueprint'}\``, '',
      '## Summary', '',
      `Critical: ${counts.critical} · High: ${counts.high} · Medium: ${counts.medium} · Low: ${counts.low} · Info: ${counts.info}`,
      '', '## Findings', ''
    ];
    if (!findings.length) lines.push('No static reliability findings detected by the current rule set.', '');
    findings.forEach((f, i) => {
      const where = f.module ? ` — module \`${f.module}\` id \`${f.module_id}\`` : '';
      lines.push(`### ${i + 1}. ${f.severity.toUpperCase()} — ${f.rule}${where}`, '', f.message, '');
    });
    lines.push(
      '## Scope limitation', '',
      'This is a static blueprint review. It cannot prove runtime correctness, third-party availability, credential validity, data quality, or business outcomes.', ''
    );
    return lines.join('\n');
  }

  return { normalizeBlueprint, walkModules, isWriteModule, scanBlueprint, summarize, renderMarkdown };
});
