(() => {
  "use strict";

  const OFFER_LABELS = Object.freeze({
    "focused-risk-check": "Focused Risk Check",
    "data-integrity-audit": "Data Integrity Audit",
    "portfolio-release-qa": "Portfolio / Release QA"
  });

  const OFFER_FILE_GUIDANCE = Object.freeze({
    "focused-risk-check": "Attach one sanitized n8n workflow JSON export.",
    "data-integrity-audit": "Attach one sanitized n8n workflow JSON export.",
    "portfolio-release-qa": "Attach up to three related sanitized n8n workflow JSON exports."
  });

  function cleanToken(value, maxLength = 120) {
    return String(value || "").replace(/[^a-zA-Z0-9_\-]/g, "").slice(0, maxLength);
  }

  function offerDisplayName(offer) {
    return OFFER_LABELS[offer] || offer || "service";
  }

  function buildIntakeMailto(params) {
    const offer = cleanToken(params.offer || "service", 40) || "service";
    const sessionId = cleanToken(params.sessionId || "unknown", 120) || "unknown";
    const displayName = offerDisplayName(offer);
    const fileGuidance = OFFER_FILE_GUIDANCE[offer] || "Attach only the sanitized n8n workflow material permitted by the purchased scope.";
    const subject = "PCFlows paid intake — " + displayName + " — " + sessionId;
    const body = [
      "Thank you for your PCFlows purchase.",
      "",
      fileGuidance,
      "",
      "Reply with:",
      "- Company:",
      "- Business outcome:",
      "- Connected systems (names only):",
      "- Current symptom or reliability concern:",
      "- n8n version and hosting type:",
      "- Approximate node count per workflow:",
      "- Acceptance condition:",
      "",
      "Safety:",
      "- Do not send plaintext credentials, tokens, customer/personal data, or confidential production logs.",
      "- Remove or replace real secrets before attaching workflow exports.",
      "",
      "Checkout reference: " + sessionId,
      "Offer: " + displayName
    ].join("\n");

    return "mailto:pcmotionstudios@gmail.com?subject=" +
      encodeURIComponent(subject) +
      "&body=" +
      encodeURIComponent(body);
  }

  function readCheckoutParams(search) {
    const qs = new URLSearchParams(search || "");
    return {
      offer: cleanToken(qs.get("offer") || "service", 40) || "service",
      sessionId: cleanToken(qs.get("session_id") || "unknown", 120) || "unknown"
    };
  }

  function bind() {
    if (typeof document === "undefined") return;
    const params = readCheckoutParams(window.location.search);
    const ref = document.getElementById("checkoutRef");
    const offer = document.getElementById("offerName");
    const button = document.getElementById("emailIntake");
    if (ref) ref.textContent = params.sessionId;
    if (offer) offer.textContent = offerDisplayName(params.offer);
    if (button) button.href = buildIntakeMailto(params);
  }

  if (typeof module !== "undefined" && module.exports) {
    module.exports = {
      OFFER_LABELS,
      OFFER_FILE_GUIDANCE,
      cleanToken,
      offerDisplayName,
      buildIntakeMailto,
      readCheckoutParams
    };
  }

  if (typeof window !== "undefined") {
    if (document.readyState === "loading") {
      document.addEventListener("DOMContentLoaded", bind);
    } else {
      bind();
    }
  }
})();
