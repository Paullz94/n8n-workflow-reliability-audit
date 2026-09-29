(() => {
  "use strict";

  const seller = Object.freeze({
    complete: false,
    legalName: "",
    tradeName: "PCFlows",
    registeredAddress: "",
    enterpriseNumber: "1043.055.054",
    vatStatus: "Confirmed by owner; numeric VAT identifier is provided to actual customers when required.",
    vatNumber: "",
    email: "pcmotionstudios@gmail.com",
    phone: ""
  });

  if (typeof window !== "undefined") {
    window.PCFLOWS_SELLER = seller;
  }

  if (typeof module !== "undefined" && module.exports) {
    module.exports = seller;
  }
})();