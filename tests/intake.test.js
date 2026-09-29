const test = require("node:test");
const assert = require("node:assert/strict");
const { buildIntakeMailto, readCheckoutParams, offerDisplayName } = require("../intake.js");

test("checkout parameters are sanitized", () => {
  const parsed = readCheckoutParams("?offer=data-integrity-audit<script>&session_id=cs_test_123%20bad");
  assert.equal(parsed.offer, "data-integrity-auditscript");
  assert.equal(parsed.sessionId, "cs_test_123bad");
});

test("canonical offer slugs render customer-facing names", () => {
  assert.equal(offerDisplayName("focused-risk-check"), "Focused Risk Check");
  assert.equal(offerDisplayName("portfolio-release-qa"), "Portfolio / Release QA");
});

test("mailto contains checkout reference, package guidance, and safety guidance", () => {
  const href = buildIntakeMailto({ offer: "portfolio-release-qa", sessionId: "cs_test_123" });
  assert.match(href, /^mailto:pcmotionstudios@gmail\.com\?/);
  const decoded = decodeURIComponent(href);
  assert.match(decoded, /cs_test_123/);
  assert.match(decoded, /up to three related sanitized n8n workflow JSON exports/);
  assert.match(decoded, /Do not send plaintext credentials/);
});
