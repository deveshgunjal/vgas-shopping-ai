// VGAS Shopping AI - WhatsApp Bot
// Developed by: Vikas Gunjal (VGAS - Vikas Gunjal Advance System)
// Phone: +91 9881300933 | Email: gunjalvikas786@gmail.com

const { default: makeWASocket, DisconnectReason, useMultiFileAuthState, fetchLatestBaileysVersion } = require("@whiskeysockets/baileys");
const { Boom } = require("@hapi/boom");
const qrcode = require("qrcode-terminal");
const axios = require("axios");
const cron = require("node-cron");
const path = require("path");
const fs = require("fs");
const pino = require("pino");

// ─────────────── CONFIG ───────────────
const CONFIG = {
  name: "VGAS Shopping AI Bot",
  backendUrl: process.env.BACKEND_URL || "http://localhost:8000",
  adminNumbers: ["919881300933@s.whatsapp.net"],
  authFolder: path.join(__dirname, "auth_info"),
  broadcastInterval: "*/30 * * * *",  // every 30 mins
  maxRetries: 3,
  version: "2.5.0",
};

// ─────────────── LOGGER (pino-compatible for Baileys) ───────────────
const baileysLogger = pino({ level: "silent" });

const log = {
  info: (msg) => console.log(`\x1b[32m[VGAS BOT]\x1b[0m ${new Date().toLocaleTimeString()} - ${msg}`),
  error: (msg) => console.error(`\x1b[31m[ERROR]\x1b[0m ${new Date().toLocaleTimeString()} - ${msg}`),
  warn: (msg) => console.warn(`\x1b[33m[WARN]\x1b[0m ${new Date().toLocaleTimeString()} - ${msg}`),
};

// ─────────────── HELPERS ───────────────
async function callBackend(endpoint, params = {}) {
  try {
    const resp = await axios.get(`${CONFIG.backendUrl}${endpoint}`, { params, timeout: 15000 });
    return resp.data;
  } catch (e) {
    log.error(`Backend call failed: ${endpoint} — ${e.message}`);
    return null;
  }
}

function formatPrice(price, currency = "₹") {
  if (!price) return "N/A";
  return `${currency}${Number(price).toLocaleString("en-IN")}`;
}

function isUrl(text) {
  return /https?:\/\/[^\s]+/.test(text);
}

function extractUrl(text) {
  const match = text.match(/https?:\/\/[^\s]+/);
  return match ? match[0] : null;
}

// ─────────────── COMMAND HANDLERS ───────────────
async function handleHelp() {
  return `🛍️ *VGAS Shopping AI Bot v${CONFIG.version}*
🏢 _Vikas Gunjal Advance System_

📋 *Commands:*

🔍 *Search Products:*
• \`find [product]\` - Best prices across all stores
• \`search [product]\` - Search any product

📊 *Compare & Check:*
• \`compare [p1] vs [p2]\` - Compare 2 products
• \`price [URL]\` - Check price of any URL
• \`fake [URL]\` - Check if discount is real/fake

💰 *Deals:*
• \`deals\` - Today's best deals (80-90% OFF)
• \`loot\` - Loot deals
• \`refurb\` - Refurbished products

📈 *Track & Alerts:*
• \`track [URL] for ₹[price]\` - Set price alert
• \`predict [URL]\` - AI price prediction

💵 *Earn Money:*
• \`earn\` - Learn about affiliate earning
• \`affiliate [URL]\` - Convert to affiliate link
• \`referral\` - Get your referral link

🌍 *Global:*
• \`global [product]\` - Compare prices worldwide
• \`currency [amount] [from] to [to]\` - Currency convert

ℹ️ *Info:*
• \`help\` - Show this menu
• \`status\` - Bot status

💡 *Tip:* Just paste any product URL and I'll analyze it automatically!

📞 Support: +91 9881300933
🌐 Website: vgas-shopping.com`;
}

async function handleSearch(query, lang = "marathi") {
  const data = await callBackend("/api/v1/search/", { query, limit: 5, sort_by: "price_asc", country: "India" });
  if (!data || !data.results?.length) {
    return `❌ "${query}" साठी कोणतेही results मिळाले नाहीत. कृपया वेगळे keyword वापरा.`;
  }

  let msg = `🔍 *"${query}" चे सर्वोत्तम किंमती:*\n\n`;
  data.results.slice(0, 5).forEach((p, i) => {
    msg += `*${i + 1}. ${p.name?.slice(0, 50) || "Product"}*\n`;
    msg += `   💰 किंमत: *${formatPrice(p.price)}* ${p.original_price > p.price ? `~~${formatPrice(p.original_price)}~~` : ""}\n`;
    msg += `   🏪 Store: ${p.store || "Online"}\n`;
    if (p.discount_percentage > 0) msg += `   🎯 Discount: *${p.discount_percentage}% OFF*\n`;
    if (p.rating) msg += `   ⭐ Rating: ${p.rating}/5\n`;
    msg += `   🔗 ${p.url?.slice(0, 60) || "#"}\n\n`;
  });

  if (data.best_price) {
    msg += `✅ *Best Deal: ${formatPrice(data.best_price)} at ${data.best_store || "Top Store"}*`;
  }
  return msg;
}

async function handlePriceCheck(url) {
  const data = await callBackend("/api/v1/products/by-url", { url });
  if (!data) return `❌ URL तपासता आले नाही. कृपया valid URL पाठवा.`;

  let msg = `🏷️ *Product Analysis:*\n\n`;
  msg += `📦 *Name:* ${data.name || "N/A"}\n`;
  msg += `💰 *Current Price:* *${formatPrice(data.price || data.current_price)}*\n`;
  if (data.original_price > (data.price || data.current_price)) {
    msg += `🔴 *Original:* ~~${formatPrice(data.original_price)}~~\n`;
    msg += `🎯 *Discount:* ${data.discount_percentage || 0}% OFF\n`;
  }
  msg += `🏪 *Store:* ${data.store || "Online"}\n`;
  if (data.rating) msg += `⭐ *Rating:* ${data.rating}/5\n`;
  if (data.fake_discount !== undefined) {
    msg += data.fake_discount
      ? `\n⚠️ *FAKE DISCOUNT DETECTED!*\nही वस्तू खरेदी करण्यापूर्वी किंमत history तपासा!`
      : `\n✅ *Discount REAL आहे!*`;
  }
  if (data.affiliate_url) msg += `\n\n💵 *Affiliate Link (कमाईसाठी):*\n${data.affiliate_url}`;
  return msg;
}

async function handleDeals(type = "loot") {
  const endpoint = type === "refurb" ? "/api/v1/search/refurbished" : "/api/v1/search/loot-deals";
  const data = await callBackend(endpoint, { limit: 5 });
  const items = Array.isArray(data) ? data : data?.results || [];

  if (!items.length) {
    return `🔥 *आजचे ${type === "refurb" ? "Refurbished" : "Loot"} Deals:*\n\n📱 iPhone 15 - ₹75,999 (was ₹89,999) - Amazon.in\n💻 MacBook Air M2 - ₹95,000 (was ₹1,19,900) - Flipkart\n🎧 Sony WH-1000XM5 - ₹19,990 (was ₹29,990) - Amazon.in\n\n🔗 vgas.app/deals आज सर्वोत्तम deals!`;
  }

  let msg = `🔥 *आजचे Best ${type === "refurb" ? "Refurbished" : "Loot"} Deals:*\n\n`;
  items.forEach((p, i) => {
    msg += `*${i + 1}. ${p.name?.slice(0, 50) || "Deal"}*\n`;
    msg += `   💰 *${formatPrice(p.price)}* ${p.discount_percentage ? `(${p.discount_percentage}% OFF!)` : ""}\n`;
    msg += `   🔗 ${p.url?.slice(0, 60) || "#"}\n\n`;
  });
  return msg;
}

async function handleEarn(from) {
  return `💰 *VGAS Shopping AI - पैसे कसे कमवाल?*

🎯 *Affiliate Program:*
• Amazon: 4-10% commission
• Flipkart: 5-10% commission  
• Myntra: 6-12% commission

📱 *Steps:*
1️⃣ vgas.app/register वर sign up करा
2️⃣ आपला referral link मिळवा
3️⃣ मित्रांना share करा
4️⃣ पैसे कमवा! 💰

💵 *Earning Potential:*
• 100 users → ₹3,000-₹5,000/month
• 1,000 users → ₹30,000-₹50,000/month
• 10,000 users → ₹3,00,000+/month

🏆 *Referral Code मिळवा:*
\`referral\` टाइप करा

📞 More info: +91 9881300933
📧 gunjalvikas786@gmail.com`;
}

async function handleAffiliate(url) {
  const data = await callBackend("/api/v1/affiliate/convert", { url, network: "amazon" });
  if (!data?.affiliate_url) {
    // Auto convert common stores
    let affUrl = url;
    if (url.includes("amazon.in")) affUrl = url + (url.includes("?") ? "&" : "?") + "tag=vgas-vikasg-21";
    else if (url.includes("flipkart.com")) affUrl = url + (url.includes("?") ? "&" : "?") + "affid=vgas2024";
    return `🔗 *Affiliate Link तयार झाली:*\n\n${affUrl}\n\n💰 हा link share केल्यावर प्रत्येक खरेदीवर commission मिळेल!`;
  }
  return `🔗 *Affiliate Link:*\n\n${data.affiliate_url}\n\n💰 Commission Rate: ${data.commission_rate || "4-10"}%\nShare करा आणि कमवा! 💵`;
}

async function handleCompare(product1, product2) {
  return `📊 *${product1} vs ${product2} - तुलना:*\n\n🔍 दोन्ही products शोधत आहे...\n\n💡 Full comparison साठी:\nvgas.app/compare?p1=${encodeURIComponent(product1)}&p2=${encodeURIComponent(product2)}\n\nकिंवा खालील command वापरा:\n\`price [URL1]\` आणि \`price [URL2]\``;
}

async function handleStatus() {
  const health = await callBackend("/health");
  const status = health?.status === "healthy" ? "🟢 Online" : "🟡 Limited";
  return `📊 *VGAS Bot Status:*\n\n🤖 Bot: 🟢 Running\n🖥️ Backend: ${status}\n📅 Time: ${new Date().toLocaleString("en-IN")}\n📦 Version: ${CONFIG.version}\n🏢 VGAS - Vikas Gunjal Advance System`;
}

// ─────────────── MESSAGE ROUTER ───────────────
async function processMessage(text, from) {
  const msg = text.trim().toLowerCase();

  // Auto URL detection
  if (isUrl(text)) {
    const url = extractUrl(text);
    return await handlePriceCheck(url);
  }

  // Commands
  if (msg.match(/^(help|h|commands|\?)$/)) return await handleHelp();
  if (msg.match(/^(status|health|ping)$/)) return await handleStatus();
  if (msg.match(/^(earn|money|affiliate program|income|referral program)$/)) return await handleEarn(from);
  if (msg.match(/^(deals|loot|offers)$/)) return await handleDeals("loot");
  if (msg.match(/^(refurb|refurbished|secondhand)$/)) return await handleDeals("refurb");

  if (msg.startsWith("find ") || msg.startsWith("search ")) {
    const q = text.replace(/^(find|search)\s+/i, "").trim();
    return await handleSearch(q);
  }
  if (msg.startsWith("price ")) {
    const url = text.replace(/^price\s+/i, "").trim();
    return isUrl(url) ? await handlePriceCheck(url) : await handleSearch(url);
  }
  if (msg.startsWith("fake ")) {
    const url = text.replace(/^fake\s+/i, "").trim();
    return await handlePriceCheck(url);
  }
  if (msg.startsWith("affiliate ") || msg.startsWith("earn link ")) {
    const url = text.replace(/^(affiliate|earn link)\s+/i, "").trim();
    return isUrl(url) ? await handleAffiliate(url) : "कृपया valid URL पाठवा.";
  }
  if (msg.includes(" vs ") || msg.startsWith("compare ")) {
    const parts = text.replace(/^compare\s+/i, "").split(/ vs /i);
    return parts.length >= 2 ? await handleCompare(parts[0].trim(), parts[1].trim()) : await handleHelp();
  }
  if (msg.match(/^(global|worldwide|international)\s+/)) {
    const q = text.replace(/^(global|worldwide|international)\s+/i, "").trim();
    return await handleSearch(q + " global price comparison");
  }
  if (msg.match(/^(hi|hello|hey|namaste|namaskar|नमस्कार|हॅलो)$/i)) {
    return `नमस्कार! 🙏\n\nमी *VGAS Shopping AI Bot* आहे.\n\nकोणताही product शोधण्यासाठी:\n• नाव टाइप करा (उदा: \`find iPhone 15\`)\n• किंवा URL पेस्ट करा\n• किंवा \`help\` टाइप करा\n\n💰 पैसे कमवण्यासाठी: \`earn\` टाइप करा`;
  }

  // Default: treat as product search
  if (msg.length > 2) return await handleSearch(text);
  return `❓ समजले नाही. \`help\` टाइप करा सर्व commands साठी.`;
}

// ─────────────── MAIN BOT ───────────────
let sock = null;

async function startBot() {
  if (!fs.existsSync(CONFIG.authFolder)) fs.mkdirSync(CONFIG.authFolder, { recursive: true });

  const { state, saveCreds } = await useMultiFileAuthState(CONFIG.authFolder);
  const { version } = await fetchLatestBaileysVersion();
  log.info(`WhatsApp v${version.join(".")} | VGAS Bot v${CONFIG.version}`);

  sock = makeWASocket({
    version,
    auth: state,
    printQRInTerminal: false,
    logger: baileysLogger,
    browser: ["VGAS Shopping AI", "Chrome", CONFIG.version],
    connectTimeoutMs: 60000,
    defaultQueryTimeoutMs: 60000,
    keepAliveIntervalMs: 25000,
  });

  sock.ev.on("creds.update", saveCreds);

  sock.ev.on("connection.update", (update) => {
    const { connection, lastDisconnect, qr } = update;

    if (qr) {
      console.log("\n\x1b[36m═══════════════════════════════════════\x1b[0m");
      console.log("\x1b[33m  📱 VGAS BOT - WhatsApp QR Code:\x1b[0m");
      console.log("\x1b[36m═══════════════════════════════════════\x1b[0m");
      qrcode.generate(qr, { small: true });
      console.log("\x1b[32m  WhatsApp > Linked Devices > Link a Device\x1b[0m");
      console.log("\x1b[36m═══════════════════════════════════════\x1b[0m\n");
    }

    if (connection === "close") {
      const shouldReconnect = (lastDisconnect?.error instanceof Boom)?.output?.statusCode !== DisconnectReason.loggedOut;
      log.warn(`Connection closed. Reconnecting: ${shouldReconnect}`);
      if (shouldReconnect) setTimeout(startBot, 5000);
    } else if (connection === "open") {
      log.info("✅ VGAS Bot connected to WhatsApp!");
      log.info(`📱 Listening for messages...`);
      setupBroadcast();
    }
  });

  sock.ev.on("messages.upsert", async (m) => {
    const msg = m.messages[0];
    if (!msg?.message || msg.key.fromMe || m.type !== "notify") return;

    const from = msg.key.remoteJid;
    const body =
      msg.message.conversation ||
      msg.message.extendedTextMessage?.text ||
      msg.message.imageMessage?.caption ||
      msg.message.videoMessage?.caption || "";

    if (!body) return;
    log.info(`Message from ${from}: ${body.slice(0, 50)}`);

    try {
      const reply = await processMessage(body, from);
      await sock.sendMessage(from, { text: reply }, { quoted: msg });
    } catch (e) {
      log.error(`Reply failed: ${e.message}`);
      await sock.sendMessage(from, { text: "❌ Error processing request. Please try again." });
    }
  });
}

function setupBroadcast() {
  cron.schedule(CONFIG.broadcastInterval, async () => {
    log.info("📢 Auto broadcast deals...");
    // Broadcast logic can be added here for groups/channels
  });
}

// Start the bot
log.info("🚀 Starting VGAS Shopping AI WhatsApp Bot...");
startBot().catch((e) => {
  log.error(`Fatal: ${e.message}`);
  process.exit(1);
});

process.on("uncaughtException", (e) => log.error(`Uncaught: ${e.message}`));
process.on("unhandledRejection", (e) => log.error(`Unhandled: ${e}`));
