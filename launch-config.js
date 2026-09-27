(() => {
  "use strict";

  const config = Object.freeze({
    checkoutEnabled: false,
    economicActivityStartAt: "2026-10-01T00:00:00+02:00",
    gates: Object.freeze({
      enterpriseRecordVerified: false,
      vatTreatmentVerified: false,
      invoicingReady: false,
      peppolReady: false,
      safeCheckoutTestPassed: false
    }),
    offers: Object.freeze({
      audit: Object.freeze({ paymentUrl: "", amountEur: 249 }),
      retrofit: Object.freeze({ paymentUrl: "", amountEur: 890 })
    })
  });

  if (typeof window !== "undefined") window.PCFLOWS_CONFIG = config;
  if (typeof module !== "undefined" && module.exports) module.exports = config;
})();
