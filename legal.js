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

  function renderSellerInfo(seller) {
    if (!sellerReady(seller)) {
      return {
        ready: false,
        html: "<p><strong>Pre-launch:</strong> final seller identity details are not yet published.</p>"
      };
    }

    const esc = value => String(value).replace(/[&<>"']/g, c => ({
      "&":"&amp;",
      "<":"&lt;",
      ">":"&gt;",
      '"':"&quot;",
      "'":"&#39;"
    }[c]));

    const vat = seller.vatNumber
      ? "<p><strong>VAT:</strong> " + esc(seller.vatNumber) + "</p>"
      : "<p><strong>VAT status:</strong> " + esc(seller.vatStatus || "Not stated") + "</p>";

    return {
      ready: true,
      html:
        "<p><strong>Legal name:</strong> " + esc(seller.legalName) + "</p>" +
        "<p><strong>Trade name:</strong> " + esc(seller.tradeName) + "</p>" +
        "<p><strong>Registered address:</strong> " + esc(seller.registeredAddress) + "</p>" +
        "<p><strong>Enterprise number:</strong> " + esc(seller.enterpriseNumber) + "</p>" +
        vat +
        "<p><strong>Email:</strong> <a href=\"mailto:" + esc(seller.email) + "\">" + esc(seller.email) + "</a></p>" +
        "<p><strong>Phone:</strong> " + esc(seller.phone) + "</p>"
    };
  }

  function bind() {
    if (typeof document === "undefined") return;
    const target = document.getElementById("sellerInfo");
    if (!target) return;
    const rendered = renderSellerInfo(window.PCFLOWS_SELLER || {});
    target.innerHTML = rendered.html;
  }

  if (typeof module !== "undefined" && module.exports) {
    module.exports = { sellerReady, renderSellerInfo };
  }

  if (typeof window !== "undefined") {
    if (document.readyState === "loading") {
      document.addEventListener("DOMContentLoaded", bind);
    } else {
      bind();
    }
  }
})();