const test = require("node:test");
const assert = require("node:assert/strict");
const { sellerReady, isLaunchReady, offerUrl } = require("../site.js");

const baseConfig = {
  checkoutEnabled: true,
  offers: {
    audit: { paymentUrl: "https://buy.stripe.com/audit" },
    retrofit: { paymentUrl: "https://buy.stripe.com/retrofit" }
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

test("launch requires checkout flag, seller identity, and both Stripe links", () => {
  assert.equal(isLaunchReady(baseConfig, baseSeller), true);
  assert.equal(isLaunchReady({ ...baseConfig, checkoutEnabled: false }, baseSeller), false);
  assert.equal(isLaunchReady(baseConfig, { ...baseSeller, complete: false }), false);
  assert.equal(isLaunchReady({ ...baseConfig, offers: { ...baseConfig.offers, audit: { paymentUrl: "" } } }, baseSeller), false);
});

test("offer URL is withheld before launch", () => {
  assert.equal(offerUrl({ ...baseConfig, checkoutEnabled: false }, baseSeller, "audit"), null);
});

test("offer URL is returned after launch gate is complete", () => {
  assert.equal(offerUrl(baseConfig, baseSeller, "retrofit"), "https://buy.stripe.com/retrofit");
});
