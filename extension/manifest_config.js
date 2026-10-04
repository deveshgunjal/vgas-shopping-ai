// VGAS Shopping AI - Chrome Extension (Manifest V3)
// Auto price comparison on any shopping site
// Developed by: Vikas Gunjal (VGAS)

const manifest = {
  "manifest_version": 3,
  "name": "VGAS Shopping AI - Price Comparer",
  "version": "1.0.0",
  "description": "Any shopping site वर automatically सर्वोत्तम किंमत दाखवतो!",
  "permissions": ["activeTab", "storage", "scripting"],
  "host_permissions": ["*://*.amazon.in/*", "*://*.flipkart.com/*", "*://*.myntra.com/*", "*://*.meesho.com/*"],
  "action": { "default_popup": "popup.html", "default_icon": "icon.png" },
  "background": { "service_worker": "background.js" },
  "content_scripts": [{
    "matches": ["*://*.amazon.in/*", "*://*.flipkart.com/*", "*://*.myntra.com/*"],
    "js": ["content.js"]
  }]
};
