/* Content Script - Auto-detect e-commerce pages */
(function() {
  "use strict";
  
  const API_BASE = "http://localhost:8000";
  
  function extractProductData() {
    const hostname = window.location.hostname;
    let data = { url: window.location.href, store: "unknown" };
    
    if (hostname.includes("amazon")) {
      data.store = "amazon";
      data.title = document.querySelector("#productTitle")?.textContent?.trim() || "";
      const priceEl = document.querySelector(".a-price-whole");
      data.price = priceEl ? parseFloat(priceEl.textContent.replace(/[^0-9.]/g, "")) : null;
      data.image = document.querySelector("#landingImage")?.src || "";
    } else if (hostname.includes("flipkart")) {
      data.store = "flipkart";
      data.title = document.querySelector("span.B_NuCI")?.textContent?.trim() || "";
      const priceText = document.querySelector("div._30jeq3._16Jk6d")?.textContent || "";
      data.price = priceText ? parseFloat(priceText.replace(/[^0-9.]/g, "")) : null;
      data.image = document.querySelector("img._396cs4")?.src || "";
    } else if (hostname.includes("ebay")) {
      data.store = "ebay";
      data.title = document.querySelector("h1.x-item-title__mainTitle")?.textContent?.trim() || "";
      const priceEl = document.querySelector(".x-price-primary span");
      data.price = priceEl ? parseFloat(priceEl.textContent.replace(/[^0-9.]/g, "")) : null;
    }
    
    return data;
  }
  
  // Send data to extension
  const productData = extractProductData();
  if (productData.price) {
    chrome.runtime.sendMessage({ type: "PRODUCT_DETECTED", data: productData });
  }
})();
