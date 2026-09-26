const test = require("node:test");
const assert = require("node:assert/strict");
const { buildIntakeMailto, readCheckoutParams } = require("../intake.js");

test("checkout parameters are sanitized", () => {
  const parsed = readCheckoutParams("?offer=audit<script>&session_id=cs_test_123%20bad");
  assert.equal(parsed.offer, "auditscript");
  assert.equal(parsed.sessionId, "cs_test_123bad");
});

test("mailto contains checkout reference and safety guidance", () => {
  const href = buildIntakeMailto({ offer: "audit", sessionId: "cs_test_123" });
  assert.match(href, /^mailto:pcmotionstudios@gmail\.com\?/);
  const decoded = decodeURIComponent(href);
  assert.match(decoded, /cs_test_123/);
  assert.match(decoded, /Do not send plaintext credentials/);
});
