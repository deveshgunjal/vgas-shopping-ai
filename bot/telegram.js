// VGAS Shopping AI - Telegram Bot
// Developed by: Vikas Gunjal (VGAS)
// Mirrors all WhatsApp Bot features on Telegram

const { Telegraf, Markup } = require("telegraf");
const axios = require("axios");

const BOT_TOKEN = process.env.TELEGRAM_BOT_TOKEN || "YOUR_BOT_TOKEN_HERE";
const BACKEND_URL = process.env.BACKEND_URL || "http://localhost:8000";

const bot = new Telegraf(BOT_TOKEN);

async function callBackend(endpoint, params = {}) {
  try {
    const res = await axios.get(`${BACKEND_URL}${endpoint}`, { params, timeout: 15000 });
    return res.data;
  } catch (e) {
    console.error(`Backend error: ${e.message}`);
    return null;
  }
}

function formatPrice(p) { return `₹${Number(p).toLocaleString("en-IN")}`; }

// /start command
bot.start((ctx) => ctx.replyWithMarkdown(`🛍️ *VGAS Shopping AI Bot*\n_Vikas Gunjal Advance System_\n\nकमांड्स:\n• /find [product] - सर्वोत्तम किंमत\n• /deals - आजचे best deals\n• /earn - पैसे कसे कमवाल\n• /modes - Auto/Manual checkout info\n\n💡 URL पेस्ट करा - मी ऑटो analysis देतो!`));

// /find command
bot.command("find", async (ctx) => {
  const query = ctx.message.text.replace("/find", "").trim();
  if (!query) return ctx.reply("कृपया product नाव सांगा. उदा: /find iPhone 15");
  ctx.reply("🔍 शोधत आहे...");
  const data = await callBackend("/api/v1/search/", { query, limit: 5 });
  if (!data?.results?.length) return ctx.reply("❌ काहीही मिळाले नाही.");
  let msg = `🔍 *${query}* चे सर्वोत्तम किंमती:\n\n`;
  data.results.slice(0, 4).forEach((p, i) => {
    msg += `*${i + 1}. ${p.name?.slice(0, 40)}*\n💰 ${formatPrice(p.price)} • 🏪 ${p.store}\n🔗 ${p.url?.slice(0, 50)}\n\n`;
  });
  ctx.replyWithMarkdown(msg);
});

// /deals command
bot.command("deals", async (ctx) => {
  const data = await callBackend("/api/v1/search/loot-deals", { limit: 4 });
  const items = Array.isArray(data) ? data : data?.results || [];
  if (!items.length) return ctx.reply("🔥 आज deals नाहीत. नंतर try करा.");
  let msg = "🔥 *आजचे Loot Deals:*\n\n";
  items.forEach((p, i) => { msg += `*${i + 1}. ${p.name?.slice(0, 40)}*\n💰 ${formatPrice(p.price)} (${p.discount_percentage}% OFF)\n\n`; });
  ctx.replyWithMarkdown(msg);
});

// /modes - Manual vs Auto Checkout info
bot.command("modes", (ctx) => ctx.replyWithMarkdown(
  `🤖 *Checkout Modes:*\n\n` +
  `1️⃣ *Manual Mode* (Recommended)\n   AI डील शोधतो, तुम्ही खरेदी करता. सुरक्षित!\n\n` +
  `2️⃣ *Auto Mode* (Power Users)\n   AI स्वतः तुमच्यासाठी ऑर्डर करतो!\n   (Saved address + payment required)\n\n` +
  `👉 Web app वर जा: vgas.app/checkout`
));

// /earn command
bot.command("earn", (ctx) => ctx.replyWithMarkdown(
  `💰 *VGAS Affiliate - पैसे कमवा!*\n\n• Amazon: 4-10% commission\n• Flipkart: 5-10%\n• Meesho: 15%\n\n📞 +91 9881300933\n📧 gunjalvikas786@gmail.com`
));

// Auto URL detection
bot.on("text", async (ctx) => {
  const text = ctx.message.text;
  if (text.startsWith("http")) {
    ctx.reply("🔍 URL analyze करत आहे...");
    const data = await callBackend("/api/v1/products/by-url", { url: text });
    if (!data) return ctx.reply("❌ URL तपासता आले नाही.");
    ctx.replyWithMarkdown(
      `🏷️ *${data.name || "Product"}*\n💰 ${formatPrice(data.price)}\n🏪 ${data.store}\n${data.fake_discount ? "⚠️ *FAKE DISCOUNT!*" : "✅ Real Discount"}`
    );
  } else if (text.length > 2) {
    // Treat as search
    const data = await callBackend("/api/v1/search/", { query: text, limit: 3 });
    if (!data?.results?.length) return ctx.reply(`❌ "${text}" साठी काही मिळाले नाही.`);
    let msg = `🔍 *${text}* results:\n\n`;
    data.results.slice(0, 3).forEach((p, i) => { msg += `${i+1}. *${p.name?.slice(0, 40)}* - ${formatPrice(p.price)}\n`; });
    ctx.replyWithMarkdown(msg);
  }
});

bot.launch();
console.log("🚀 VGAS Telegram Bot started!");
process.once("SIGINT", () => bot.stop("SIGINT"));
