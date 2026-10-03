// VGAS Shopping AI - Telegram Bot
// Developed by: Vikas Gunjal (VGAS)

const { Telegraf, Markup } = require('telegraf');
const axios = require('axios');

const BOT_TOKEN = process.env.TELEGRAM_BOT_TOKEN;
const API_BASE = process.env.VGAS_API_BASE || 'http://localhost:8000/api/v1';

const bot = new Telegraf(BOT_TOKEN);

bot.start((ctx) => ctx.reply('Welcome to VGAS Shopping Bot! Use /menu to explore.'));

bot.command('menu', async (ctx) => {
  const menu = Markup.inlineKeyboard([
    [Markup.button.callback('Browse Products', 'browse')],
    [Markup.button.callback('My Cart', 'cart')],
    [Markup.button.callback('Checkout', 'checkout')]
  ]);
  await ctx.reply('Select an option:', menu);
});

bot.action('browse', async (ctx) => {
  // Fetch categories
  const res = await axios.get(`${API_BASE}/products/categories`);
  const cats = res.data.map(c => Markup.button.callback(c.name, `cat_${c.id}`));
  await ctx.reply('Categories:', Markup.inlineKeyboard(cats.map(b => [b])));
});

bot.action(/cat_(\d+)/, async (ctx) => {
  const catId = ctx.match[1];
  const res = await axios.get(`${API_BASE}/products?category=${catId}`);
  const items = res.data.map(p => Markup.button.callback(p.title, `prod_${p.id}`));
  await ctx.reply('Products:', Markup.inlineKeyboard(items.map(b => [b])));
});

bot.action(/prod_(\d+)/, async (ctx) => {
  const prodId = ctx.match[1];
  const res = await axios.get(`${API_BASE}/products/${prodId}`);
  const p = res.data;
  await ctx.reply(`${p.title}\nPrice: ${p.price}\n${p.description}`);
  // Add to cart
  await ctx.reply('Add to cart?', Markup.inlineKeyboard([
    Markup.button.callback('Add', `add_${p.id}`),
    Markup.button.callback('Cancel', 'cancel')
  ]));
});

bot.action(/add_(\d+)/, async (ctx) => {
  const prodId = ctx.match[1];
  await axios.post(`${API_BASE}/cart/add`, { product_id: prodId, quantity: 1 }, { headers: { Authorization: `Bearer ${ctx.session.token}` } });
  await ctx.reply('Added to cart!');
});

bot.action('cart', async (ctx) => {
  const res = await axios.get(`${API_BASE}/cart`, { headers: { Authorization: `Bearer ${ctx.session.token}` } });
  const items = res.data.items.map(i => `${i.title} x${i.quantity}`).join('\n');
  await ctx.reply(`Your Cart:\n${items}`);
});

bot.action('checkout', async (ctx) => {
  // Offer manual or auto mode
  await ctx.reply('Choose checkout mode:', Markup.inlineKeyboard([
    Markup.button.callback('Manual Review', 'checkout_manual'),
    Markup.button.callback('Auto Checkout', 'checkout_auto')
  ]));
});

bot.action('checkout_manual', async (ctx) => {
  const res = await axios.post(`${API_BASE}/checkout/manual`, {}, { headers: { Authorization: `Bearer ${ctx.session.token}` } });
  await ctx.reply(`Order placed. Order ID: ${res.data.order_id}`);
});

bot.action('checkout_auto', async (ctx) => {
  const res = await axios.post(`${API_BASE}/checkout/auto`, {}, { headers: { Authorization: `Bearer ${ctx.session.token}` } });
  await ctx.reply(`Auto order placed. Order ID: ${res.data.order_id}`);
});

bot.launch();

process.once('SIGINT', () => bot.stop('SIGINT'));
process.once('SIGTERM', () => bot.stop('SIGTERM'));
