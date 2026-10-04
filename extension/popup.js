/* Popup Script */
const API_BASE = "http://localhost:8000";

document.addEventListener("DOMContentLoaded", () => {
  chrome.storage.local.get(["currentProduct", "priceData"], (result) => {
    if (result.currentProduct) {
      const product = result.currentProduct;
      
      document.getElementById("no-product").classList.add("hidden");
      document.getElementById("product-info").classList.remove("hidden");
      document.getElementById("watch-btn").classList.remove("hidden");
      document.getElementById("compare-btn").classList.remove("hidden");
      
      document.getElementById("product-title").textContent = product.title || "Unknown Product";
      document.getElementById("product-price").textContent = product.price ? `${product.price}` : "N/A";
      
      if (product.image) {
        document.getElementById("product-image").src = product.image;
      }
      
      // Price badge
      const badge = document.getElementById("price-badge");
      if (result.priceData?.verdict) {
        badge.textContent = result.priceData.verdict;
        badge.className = "text-xs px-2 py-0.5 rounded-full " + 
          (result.priceData.verdict === "BEST" ? "badge-good" : 
           result.priceData.verdict === "GOOD" ? "badge-good" : "badge-ok");
      }
    }
  });
  
  // Watch button
  document.getElementById("watch-btn").addEventListener("click", () => {
    chrome.storage.local.get("currentProduct", (result) => {
      if (result.currentProduct) {
        chrome.runtime.sendMessage({
          type: "WATCH_PRODUCT",
          data: {
            url: result.currentProduct.url,
            title: result.currentProduct.title,
            target_price: result.currentProduct.price * 0.9,
          }
        }, (response) => {
          alert(response?.id ? "Added to watchlist!" : "Error adding to watchlist");
        });
      }
    });
  });
  
  // Compare button
  document.getElementById("compare-btn").addEventListener("click", () => {
    chrome.storage.local.get("currentProduct", (result) => {
      if (result.currentProduct) {
        window.open(`${API_BASE}/api/v1/compare?url=${encodeURIComponent(result.currentProduct.url)}`, "_blank");
      }
    });
  });
});
