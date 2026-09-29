const test = require("node:test");
const assert = require("node:assert/strict");
const {
  sellerReady,
  commercialStartReached,
  offersReady,
  isLaunchReady,
  offerUrl
} = require("../site.js");

const launchMs = Date.parse("2026-10-01T00:00:00+02:00");
const preLaunchMs = Date.parse("2026-09-30T23:59:59+02:00");

const baseConfig = {
  checkoutEnabled: true,
  commercialStartAt: "2026-10-01T00:00:00+02:00",
  offers: {
    focusedRiskCheck: { paymentUrl: "https://buy.stripe.com/focused", amountEur: 79 },
    dataIntegrityAudit: { paymentUrl: "https://buy.stripe.com/audit", amountEur: 149 },
    portfolioReleaseQa: { paymentUrl: "https://buy.stripe.com/portfolio", amountEur: 399 }
  }
};

const baseSeller = {
  complete: true,
  legalName: "Example SRL",
  tradeName: "PCFlows",
  registeredAddress: "Example Street 1",
  enterpriseNumber: "0123.456.789",
  email: "business@example.com",
  phone: "+32000000000"
};

test("seller readiness requires explicit completion and public identity fields", () => {
  assert.equal(sellerReady(baseSeller), true);
  assert.equal(sellerReady({ ...baseSeller, complete: false }), false);
  assert.equal(sellerReady({ ...baseSeller, enterpriseNumber: "" }), false);
});

test("commercial start date is a hard gate", () => {
  assert.equal(commercialStartReached(baseConfig, preLaunchMs), false);
  assert.equal(commercialStartReached(baseConfig, launchMs), true);
});

test("all three canonical Stripe offers are required", () => {
  assert.equal(offersReady(baseConfig), true);
  assert.equal(
    offersReady({
      ...baseConfig,
      offers: { ...baseConfig.offers, dataIntegrityAudit: { paymentUrl: "", amountEur: 149 } }
    }),
    false
  );
});

test("launch requires date, checkout switch, seller identity, and all Stripe links", () => {
  assert.equal(isLaunchReady(baseConfig, baseSeller, launchMs), true);
  assert.equal(isLaunchReady(baseConfig, baseSeller, preLaunchMs), false);
  assert.equal(isLaunchReady({ ...baseConfig, checkoutEnabled: false }, baseSeller, launchMs), false);
  assert.equal(isLaunchReady(baseConfig, { ...baseSeller, complete: false }, launchMs), false);
});

test("offer URL is withheld before launch", () => {
  assert.equal(offerUrl(baseConfig, baseSeller, "focusedRiskCheck", preLaunchMs), null);
});

test("offer URL is returned only after the complete launch gate", () => {
  assert.equal(
    offerUrl(baseConfig, baseSeller, "portfolioReleaseQa", launchMs),
    "https://buy.stripe.com/portfolio"
  );
});
