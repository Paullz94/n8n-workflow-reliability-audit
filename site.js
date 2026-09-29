(() => {
  "use strict";

  const REQUIRED_OFFERS = Object.freeze([
    "focusedRiskCheck",
    "dataIntegrityAudit",
    "portfolioReleaseQa"
  ]);

  function sellerReady(seller) {
    if (!seller || seller.complete !== true) return false;
    const required = [
      seller.legalName,
      seller.tradeName,
      seller.registeredAddress,
      seller.enterpriseNumber,
      seller.email,
      seller.phone
    ];
    return required.every(value => String(value || "").trim().length > 0);
  }

  function commercialStartReached(config, nowMs = Date.now()) {
    if (!config || !config.commercialStartAt) return false;
    const startMs = Date.parse(config.commercialStartAt);
    return Number.isFinite(startMs) && nowMs >= startMs;
  }

  function offersReady(config) {
    if (!config || !config.offers) return false;
    return REQUIRED_OFFERS.every(key => {
      const offer = config.offers[key];
      return Boolean(
        offer &&
        Number(offer.amountEur) > 0 &&
        /^https:\/\/buy\.stripe\.com\//.test(offer.paymentUrl || "")
      );
    });
  }

  function isLaunchReady(config, seller, nowMs = Date.now()) {
    return Boolean(
      config &&
      config.checkoutEnabled === true &&
      commercialStartReached(config, nowMs) &&
      sellerReady(seller) &&
      offersReady(config)
    );
  }

  function offerUrl(config, seller, offer, nowMs = Date.now()) {
    if (!isLaunchReady(config, seller, nowMs)) return null;
    return config.offers[offer] && config.offers[offer].paymentUrl || null;
  }

  function statusMessage(config, seller, nowMs = Date.now()) {
    if (!commercialStartReached(config, nowMs)) {
      return "<strong>Pre-launch checkout staged:</strong> paid service, payment acceptance and invoicing begin no earlier than 1 October 2026.";
    }
    if (!sellerReady(seller)) {
      return "<strong>Checkout held:</strong> the remaining public seller identity fields must be completed before paid checkout can open.";
    }
    if (!config || config.checkoutEnabled !== true) {
      return "<strong>Checkout staged:</strong> the canonical Stripe links are prepared but remain disabled until the operational launch gate is switched on.";
    }
    if (!offersReady(config)) {
      return "<strong>Checkout held:</strong> one or more canonical Stripe offer links are missing or invalid.";
    }
    return "<strong>Checkout live:</strong> fixed-scope B2B checkout is available below.";
  }

  function bindLaunchState() {
    if (typeof document === "undefined") return;
    const config = window.PCFLOWS_CONFIG || {};
    const seller = window.PCFLOWS_SELLER || {};
    const nowMs = Date.now();
    const ready = isLaunchReady(config, seller, nowMs);
    const status = document.getElementById("launchStatus");

    for (const el of document.querySelectorAll("[data-checkout-offer]")) {
      const url = offerUrl(config, seller, el.getAttribute("data-checkout-offer"), nowMs);
      if (ready && url) {
        el.href = url;
        el.hidden = false;
        el.setAttribute("rel", "noopener");
      } else {
        el.hidden = true;
        el.removeAttribute("href");
      }
    }

    if (status) status.innerHTML = statusMessage(config, seller, nowMs);
  }

  if (typeof module !== "undefined" && module.exports) {
    module.exports = {
      REQUIRED_OFFERS,
      sellerReady,
      commercialStartReached,
      offersReady,
      isLaunchReady,
      offerUrl,
      statusMessage
    };
  }

  if (typeof window !== "undefined") {
    if (document.readyState === "loading") {
      document.addEventListener("DOMContentLoaded", bindLaunchState);
    } else {
      bindLaunchState();
    }
  }
})();
