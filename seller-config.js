(() => {
  "use strict";

  const seller = Object.freeze({
    complete: false,
    legalName: "",
    tradeName: "PCFlows",
    registeredAddress: "",
    enterpriseNumber: "",
    vatStatus: "",
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