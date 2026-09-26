(() => {
  "use strict";

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

  function isLaunchReady(config, seller) {
    return Boolean(
      config &&
      config.checkoutEnabled === true &&
      sellerReady(seller) &&
      config.offers &&
      config.offers.audit &&
      /^https:\/\/buy\.stripe\.com\//.test(config.offers.audit.paymentUrl || "") &&
      config.offers.retrofit &&
      /^https:\/\/buy\.stripe\.com\//.test(config.offers.retrofit.paymentUrl || "")
    );
  }

  function offerUrl(config, seller, offer) {
    if (!isLaunchReady(config, seller)) return null;
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
        el.href = url;
        el.hidden = false;
        el.setAttribute("rel", "noopener");
      } else {
        el.hidden = true;
        el.removeAttribute("href");
      }
    }

    if (status) {
      status.innerHTML = ready
        ? "<strong>Checkout live:</strong> fixed-scope B2B checkout is available below."
        : "<strong>Technical checkout staged:</strong> Stripe checkout is configured but remains hidden until the final seller identity details are published.";
    }
  }

  if (typeof module !== "undefined" && module.exports) {
    module.exports = { sellerReady, isLaunchReady, offerUrl };
  }

  if (typeof window !== "undefined") {
    if (document.readyState === "loading") {
      document.addEventListener("DOMContentLoaded", bindLaunchState);
    } else {
      bindLaunchState();
    }
  }
})();