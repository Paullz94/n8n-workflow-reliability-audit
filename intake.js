(() => {
  "use strict";

  function cleanToken(value, maxLength = 120) {
    return String(value || "").replace(/[^a-zA-Z0-9_\-]/g, "").slice(0, maxLength);
  }

  function buildIntakeMailto(params) {
    const offer = cleanToken(params.offer || "service", 24) || "service";
    const sessionId = cleanToken(params.sessionId || "unknown", 120) || "unknown";
    const subject = "PCFlows paid intake — " + offer + " — " + sessionId;
    const body = [
      "Thank you for your PCFlows purchase.",
      "",
      "Please attach ONE sanitized n8n workflow JSON export to this email.",
      "",
      "Reply with:",
      "- Company:",
      "- Business outcome:",
      "- Connected systems (names only):",
      "- Current symptom or reliability concern:",
      "- n8n version and hosting type:",
      "- Approximate node count:",
      "- Acceptance condition:",
      "",
      "Safety:",
      "- Do not send plaintext credentials, tokens, customer/personal data, or confidential production logs.",
      "- Remove or replace real secrets before attaching the workflow export.",
      "",
      "Checkout reference: " + sessionId,
      "Offer: " + offer
    ].join("\n");

    return "mailto:pcmotionstudios@gmail.com?subject=" +
      encodeURIComponent(subject) +
      "&body=" +
      encodeURIComponent(body);
  }

  function readCheckoutParams(search) {
    const qs = new URLSearchParams(search || "");
    return {
      offer: cleanToken(qs.get("offer") || "service", 24) || "service",
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
    if (offer) offer.textContent = params.offer;
    if (button) button.href = buildIntakeMailto(params);
  }

  if (typeof module !== "undefined" && module.exports) {
    module.exports = { cleanToken, buildIntakeMailto, readCheckoutParams };
  }

  if (typeof window !== "undefined") {
    if (document.readyState === "loading") {
      document.addEventListener("DOMContentLoaded", bind);
    } else {
      bind();
    }
  }
})();