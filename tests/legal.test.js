const test = require("node:test");
const assert = require("node:assert/strict");
const { sellerReady, renderSellerInfo } = require("../legal.js");

const completeSeller = {
  complete: true,
  legalName: "Example SRL",
  tradeName: "PCFlows",
  registeredAddress: "Example Street 1, 1000 Brussels, Belgium",
  enterpriseNumber: "0123.456.789",
  vatStatus: "VAT registered",
  vatNumber: "BE0123456789",
  email: "business@example.com",
  phone: "+32000000000"
};

test("seller identity stays closed when required fields are absent", () => {
  assert.equal(sellerReady({ ...completeSeller, enterpriseNumber: "" }), false);
  assert.equal(sellerReady({ ...completeSeller, complete: false }), false);
});

test("seller identity renders escaped public fields", () => {
  const rendered = renderSellerInfo({ ...completeSeller, legalName: "<Example>" });
  assert.equal(rendered.ready, true);
  assert.match(rendered.html, /&lt;Example&gt;/);
  assert.doesNotMatch(rendered.html, /<Example>/);
});


test("partial pre-launch identity may publish the confirmed enterprise number without opening checkout", () => {
  const rendered = renderSellerInfo({
    complete: false,
    tradeName: "PCFlows",
    enterpriseNumber: "1043055054",
    email: "pcmotionstudios@gmail.com"
  });
  assert.equal(rendered.ready, false);
  assert.match(rendered.html, /1043055054/);
  assert.match(rendered.html, /paid checkout remains disabled/);
});
