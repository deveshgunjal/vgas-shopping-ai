/* Background Service Worker */
const API_BASE = "http://localhost:8000";

chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
  if (message.type === "PRODUCT_DETECTED") {
    chrome.storage.local.set({ currentProduct: message.data });
    
    // Check price via API
    fetch(`${API_BASE}/api/v1/extension/price?url=${encodeURIComponent(message.data.url)}`)
      .then(res => res.json())
      .then(data => {
        chrome.storage.local.set({ priceData: data });
      })
      .catch(err => console.error("API Error:", err));
  }
  
  if (message.type === "WATCH_PRODUCT") {
    fetch(`${API_BASE}/api/v1/extension/watch`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(message.data),
    })
      .then(res => res.json())
      .then(data => sendResponse(data))
      .catch(err => sendResponse({ error: err.message }));
    
    return true; // Keep message channel open for async response
  }
});

// Price check alarm
chrome.alarms.create("priceCheck", { periodInMinutes: 60 });

chrome.alarms.onAlarm.addListener((alarm) => {
  if (alarm.name === "priceCheck") {
    chrome.storage.local.get("watchlist", (result) => {
      const watchlist = result.watchlist || [];
      watchlist.forEach(item => {
        fetch(`${API_BASE}/api/v1/price-history/${item.product_id}`)
          .then(res => res.json())
          .then(data => {
            if (data.length > 0) {
              const latest = data[data.length - 1];
              if (latest.price <= item.target_price) {
                chrome.notifications.create({
                  type: "basic",
                  title: "Price Drop Alert!",
                  message: `${item.title} is now ${latest.price}!`,
                  iconUrl: "icons/icon128.png",
                });
              }
            }
          });
      });
    });
  }
});
