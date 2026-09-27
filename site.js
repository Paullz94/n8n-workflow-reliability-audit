(() => {
  "use strict";
  function sellerReady(seller) {
    if (!seller || seller.complete !== true) return false;
    const required = [seller.legalName, seller.tradeName, seller.registeredAddress, seller.enterpriseNumber, seller.vatStatus, seller.email, seller.phone];
    return required.every(value => String(value || "").trim().length > 0);
  }
  function launchGatesReady(config) {
    const gates = config && config.gates;
    return Boolean(gates &&
      gates.enterpriseRecordVerified === true &&
      gates.vatTreatmentVerified === true &&
      gates.invoicingReady === true &&
      gates.peppolReady === true &&
      gates.safeCheckoutTestPassed === true);
  }
  function activityStartReached(config, now = new Date()) {
    const start = Date.parse(config && config.economicActivityStartAt || "");
    const current = now instanceof Date ? now.getTime() : Date.parse(now);
    return Number.isFinite(start) && Number.isFinite(current) && current >= start;
  }
  function isLaunchReady(config, seller, now = new Date()) {
    return Boolean(
      config &&
      config.checkoutEnabled === true &&
      activityStartReached(config, now) &&
      launchGatesReady(config) &&
      sellerReady(seller) &&
      config.offers &&
      config.offers.audit &&
      /^https:\/\/buy\.stripe\.com\//.test(config.offers.audit.paymentUrl || "") &&
      config.offers.retrofit &&
      /^https:\/\/buy\.stripe\.com\//.test(config.offers.retrofit.paymentUrl || ""));
  }
  function offerUrl(config, seller, offer, now = new Date()) {
    if (!isLaunchReady(config, seller, now)) return null;
    return config.offers[offer] && config.offers[offer].paymentUrl || null;
  }
  function bindLaunchState() {
    if (typeof document === "undefined") return;
    const config = window.PCFLOWS_CONFIG || {};
    const seller = window.PCFLOWS_SELLER || {};
    const ready = isLaunchReady(config, seller);
    const status = document.getElementById("launchStatus");
    for (const el of document.querySelectorAll("[data-checkout-offer]")) {
      const url = offerUrl(config, seller, el.getAttribute("data-checkout-offer"));
      if (ready && url) {
        el.href = url; el.hidden = false; el.setAttribute("rel", "noopener");
      } else {
        el.hidden = true; el.removeAttribute("href");
      }
    }
    if (status) {
      status.innerHTML = ready
        ? "<strong>Checkout live:</strong> fixed-scope B2B checkout is available below."
        : "<strong>Paid checkout unavailable:</strong> launch remains gated by official registration, VAT treatment, public seller identity, invoicing/Peppol readiness, the economic-activity start date and a safe checkout test.";
    }
  }
  if (typeof module !== "undefined" && module.exports) {
    module.exports = { sellerReady, launchGatesReady, activityStartReached, isLaunchReady, offerUrl };
  }
  if (typeof window !== "undefined") {
    if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", bindLaunchState);
    else bindLaunchState();
  }
})();
