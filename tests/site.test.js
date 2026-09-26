const test = require("node:test");
const assert = require("node:assert/strict");
const { isLaunchReady, offerUrl } = require("../site.js");

const base = {
  checkoutEnabled: true,
  businessIdentityComplete: true,
  offers: {
    audit: { paymentUrl: "https://buy.stripe.com/audit" },
    retrofit: { paymentUrl: "https://buy.stripe.com/retrofit" }
  }
};

test("launch requires both explicit flags and both Stripe links", () => {
  assert.equal(isLaunchReady(base), true);
  assert.equal(isLaunchReady({ ...base, checkoutEnabled: false }), false);
  assert.equal(isLaunchReady({ ...base, businessIdentityComplete: false }), false);
  assert.equal(isLaunchReady({ ...base, offers: { ...base.offers, audit: { paymentUrl: "" } } }), false);
});

test("offer URL is withheld before launch", () => {
  assert.equal(offerUrl({ ...base, checkoutEnabled: false }, "audit"), null);
});

test("offer URL is returned after launch gate is complete", () => {
  assert.equal(offerUrl(base, "retrofit"), "https://buy.stripe.com/retrofit");
});
