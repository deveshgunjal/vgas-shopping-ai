# VGAS Shopping AI - Vikas Gunjal Advance System

## Global Shopping Price Comparison & AI Assistant Platform

**Version:** 2.5.0  
**Developer:** Vikas Gunjal  
**Email:** gunjalvikas786@gmail.com  
**Phone:** +91 9881300933  
**Company:** VGAS - Vikas Gunjal Advance System  
**Location:** Chhatrapati Sambhaji Nagar, Maharashtra, India  

---

## Table of Contents

1. [Overview](#overview)
2. [Features](#features)
3. [Project Structure](#project-structure)
4. [Quick Start](#quick-start)
5. [Installation](#installation)
6. [Configuration](#configuration)
7. [API Endpoints](#api-endpoints)
8. [Scrapers](#scrapers)
9. [AI Assistant](#ai-assistant)
10. [Monetization](#monetization)
11. [WhatsApp Bot](#whatsapp-bot)
12. [Frontend Integration](#frontend-integration)
13. [Deployment](#deployment)
14. [Comparison with Similar Apps](#comparison-with-similar-apps)
15. [Roadmap](#roadmap)
16. [Support](#support)

---

## Overview

VGAS Shopping AI is the world's first **24+ language AI shopping assistant** that helps users:
- Find the **lowest prices** across 100+ e-commerce platforms
- **Detect fake discounts** using AI-powered price history analysis
- **Compare products** side-by-side with detailed specifications
- **Earn money** through affiliate marketing and referrals
- Get **personalized recommendations** based on preferences
- Track **price drops** and get instant alerts

The platform supports **India, USA, UK, Germany, Japan, UAE, Canada, Australia, Singapore, and 190+ countries** with multi-currency and multi-language support.

---

## Features

### Core Features

✅ **Global Price Comparison** - Search products across Amazon (IN/US/UK/DE/JP/AE), Flipkart, Myntra, Ajio, Walmart, eBay, AliExpress, Noon, and 100+ stores

✅ **Direct Product Name Search** - Users can search by typing product names (e.g., "iPhone 15", "TV", "Laptop") instead of just pasting URLs

✅ **Fake Discount Detection** - AI analyzes price history to detect artificially inflated prices before sales

✅ **Multi-Currency Support** - USD, EUR, GBP, INR, AED, CAD, AUD, SGD, SAR, QAR, and more

✅ **24+ Language Support** - Marathi, Hindi, English, Tamil, Telugu, Bengali, Gujarati, Kannada, Punjabi, Malayalam, Odia, Arabic, Spanish, French, German, Chinese, Japanese

✅ **Affiliate Link Conversion** - Automatically converts product links to earning links (Amazon, Flipkart, Myntra, EarnKaro, Cuelinks)

✅ **WhatsApp Bot Integration** - Users can search products via WhatsApp messages

✅ **AI Shopping Assistant** - Chat with AI for product recommendations, price comparisons, and shopping advice

✅ **Price Drop Alerts** - Get notified when tracked products' prices decrease

✅ **Side-by-Side Product Comparison** - Compare multiple products with detailed feature comparison

✅ **VIP Membership** - Ad-free experience with exclusive deals and early access

✅ **PayPal Integration** - Receive earnings globally in multiple currencies

✅ **Razorpay Payment Gateway** - Support for UPI, Cards, Net Banking, and COD

---

## Project Structure

```
VGAS_Project/
├── backend/                  # FastAPI Backend Server
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py           # FastAPI application
│   │   ├── core/
│   │   │   ├── __init__.py
│   │   │   ├── config.py     # Settings & configuration
│   │   │   ├── database.py   # Database models (SQLAlchemy)
│   │   │   └── redis_cache.py # Redis caching
│   │   ├── api/
│   │   │   └── v1/
│   │   │       ├── __init__.py
│   │   │       ├── search.py      # Product search endpoints
│   │   │       ├── products.py    # Product details endpoints
│   │   │       ├── compare.py     # Product comparison endpoints
│   │   │       ├── affiliate.py   # Affiliate marketing endpoints
│   │   │       ├── ai.py          # AI assistant endpoints
│   │   │       ├── monetization.py # Revenue generation endpoints
│   │   │       └── whatsapp.py    # WhatsApp bot endpoints
│   │   ├── scrapers/
│   │   │   ├── __init__.py
│   │   │   ├── base_scraper.py   # Base scraper class
│   │   │   ├── search_engine.py  # Product search engine
│   │   │   ├── amazon_scraper.py # Amazon scraper
│   │   │   ├── flipkart_scraper.py
│   │   │   ├── myntra_scraper.py
│   │   │   ├── ajio_scraper.py
│   │   │   └── global_scrapers.py
│   │   ├── services/
│   │   │   └── scheduler.py    # Background tasks
│   │   └── utils/
│   │       ├── __init__.py
│   │       └── logger.py      # Logging configuration
│   ├── requirements.txt
│   └── .env.example
├── bot/                      # WhatsApp Bot (Node.js)
├── web/                      # Frontend (React/Vue)
├── shopping-ai/             # Android App (Existing)
└── README.md
```

---

## Quick Start

### Prerequisites

- Python 3.10+
- PostgreSQL 14+
- Redis 7+
- Node.js 18+ (for WhatsApp bot and frontend)
- Playwright (for web scraping)

### 3 Steps to Run VGAS Shopping AI

#### Step 1: Install Dependencies

```bash
# Navigate to backend directory
cd D:/Sam/VGAS_Project/backend

# Install Python dependencies
pip install -r requirements.txt

# Install Playwright browsers
playwright install chromium

# Create and activate virtual environment (recommended)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

#### Step 2: Configure Environment

```bash
# Copy example environment file
cp .env.example .env

# Edit .env file with your settings
nano .env  # Or use any text editor

# Key settings to configure:
# - POSTGRES_USER, POSTGRES_PASSWORD, POSTGRES_DB
# - REDIS_URL
# - AMAZON_AFFILIATE_ID, FLIPKART_AFFILIATE_ID
# - PAYPAL_BUSINESS_EMAIL
# - WHATSAPP_PHONE_NUMBER
```

#### Step 3: Start Services

```bash
# Start PostgreSQL (Windows)
net start postgresql

# Start Redis (in new terminal)
redis-server

# Start backend (in new terminal)
cd D:/Sam/VGAS_Project/backend
uvicorn app.main:app --reload --port 8000

# The API will be available at: http://localhost:8000
# API Documentation: http://localhost:8000/docs
```

---

## Installation

### 1. Clone/Setup the Project

The project is already created at `D:/Sam/VGAS_Project` with the following structure:

```bash
VGAS_Project/
├── backend/      # FastAPI backend
├── bot/          # WhatsApp bot (to be created)
└── web/          # Frontend (to be created)
```

### 2. Install Backend Dependencies

```bash
cd backend
pip install -r requirements.txt
playwright install chromium
```

### 3. Setup Database

```bash
# Install PostgreSQL from: https://www.postgresql.org/download/

# Create database
createdb vgas_shopping

# Or using psql:
psql -U postgres -c "CREATE DATABASE vgas_shopping;"
```

### 4. Run Database Migrations

The SQLAlchemy models will automatically create tables on first run. No separate migration needed.

### 5. Start Redis

```bash
# Install Redis from: https://redis.io/download
redis-server
```

---

## Configuration

Edit `.env` file in the backend directory:

```ini
# Server Configuration
APP_NAME=VGAS Shopping AI
APP_VERSION=2.5.0
DEBUG=True
PORT=8000

# Database Configuration
POSTGRES_USER=postgres
POSTGRES_PASSWORD=your_password
POSTGRES_DB=vgas_shopping
POSTGRES_HOST=localhost
POSTGRES_PORT=5432

# Redis Configuration
REDIS_URL=redis://localhost:6379/0

# API Keys
GEMINI_API_KEY=your_gemini_api_key_here
OPENAI_API_KEY=your_openai_api_key_here

# Affiliate IDs
AMAZON_AFFILIATE_ID=vgas-vikasg-21
FLIPKART_AFFILIATE_ID=your_flipkart_id
EARNKARO_API_KEY=your_earnkaro_key

# WhatsApp Bot
WHATSAPP_BOT_TOKEN=your_whatsapp_token
WHATSAPP_PHONE_NUMBER=919881300933

# PayPal
PAYPAL_BUSINESS_EMAIL=gunjalvikas786@gmail.com
PAYPAL_API_CLIENT_ID=your_paypal_client_id
PAYPAL_API_SECRET=your_paypal_secret
PAYPAL_MODE=sandbox  # Change to 'live' for production

# Security
SECRET_KEY=vgas-super-secret-key-2024
```

---

## API Endpoints

### Base URL: `http://localhost:8000`

### Health Check
- `GET /` - Welcome message
- `GET /health` - Health check
- `GET /info` - Detailed app information

### Search API (`/api/v1/search/`)
- `GET /` - Search products by name
- `GET /quick` - Quick search with limited results
- `GET /autocomplete` - Get search suggestions
- `GET /trending` - Get trending products
- `GET /loot-deals` - Get 80-90% discount deals
- `GET /refurbished` - Get refurbished products
- `GET /categories` - Get product categories
- `GET /stores` - Get supported stores

### Products API (`/api/v1/products/`)
- `GET /by-url` - Get product details by URL
- `GET /by-id` - Get product by ID/ASIN
- `POST /by-image` - Search by image
- `POST /by-voice` - Search by voice
- `GET /details` - Get detailed product info
- `GET /batch` - Get multiple products

### Comparison API (`/api/v1/compare/`)
- `POST /` - Compare multiple products
- `GET /quick` - Quick compare by URLs
- `POST /by-query` - Compare by product names

### Affiliate API (`/api/v1/affiliate/`)
- `GET /convert` - Convert URL to affiliate URL
- `POST /batch` - Batch convert URLs
- `GET /redirect` - Redirect to affiliate URL
- `GET /stats` - Get affiliate statistics
- `GET /link-info` - Analyze affiliate link

### AI Assistant API (`/api/v1/ai/`)
- `GET /chat` - Start chat session
- `POST /chat/send` - Send message to AI
- `GET /chat/history` - Get chat history
- `WS /chat/ws` - WebSocket chat
- `POST /analyze` - Analyze product/deal/review
- `GET /recommend` - Get product recommendations
- `GET /translate` - Translate text

### WhatsApp API (`/api/v1/whatsapp/`)
- `POST /webhook` - Receive WhatsApp messages
- `GET /verify` - Verify WhatsApp webhook
- `POST /send` - Send WhatsApp message
- `POST /broadcast` - Broadcast to multiple users
- `POST /process-message` - Process message directly

### Monetization API (`/api/v1/monetization/`)
- `GET /stats` - Get monetization statistics
- `GET /revenue` - Get revenue breakdown
- `GET /affiliate-links` - Get top affiliate links
- `GET /earnings` - Estimate earnings
- `GET /payouts` - Get payout information
- `POST /referral/generate` - Generate referral link
- `GET /referral/stats` - Get referral statistics
- `GET /vip` - Get VIP membership info

---

## API Usage Examples

### 1. Search Products by Name (Main Feature)

```bash
# Search for "iPhone 15" in India
curl "http://localhost:8000/api/v1/search/?query=iPhone%2015&country=India&limit=10&sort_by=price_asc"

# Search with filters
curl "http://localhost:8000/api/v1/search/?query=TV&min_price=20000&max_price=50000&brand=Samsung"
```

**Response:** Returns list of products from all stores with prices, discounts, ratings, etc.

### 2. Get Product Details by URL

```bash
curl "http://localhost:8000/api/v1/products/by-url?url=https://www.amazon.in/dp/B123456789"
```

**Response:** Returns comprehensive product information including fake discount detection.

### 3. Compare Products

```bash
# Compare multiple URLs
curl -X POST http://localhost:8000/api/v1/compare/ \
  -H "Content-Type: application/json" \
  -d '{"urls": ["https://amazon.in/...", "https://flipkart.com/..."]}'

# Compare by product names
curl -X POST http://localhost:8000/api/v1/compare/by-query \
  -H "Content-Type: application/json" \
  -d '{"products": [{"name": "iPhone 15", "brand": "Apple"}, {"name": "Galaxy S24", "brand": "Samsung"}]}'
```

**Response:** Returns detailed comparison with best deal recommendation.

### 4. Convert to Affiliate URL

```bash
curl "http://localhost:8000/api/v1/affiliate/convert?url=https://amazon.in/dp/B123456789&network=amazon"
```

**Response:** Returns affiliate URL with commission tracking.

### 5. Chat with AI Assistant

```bash
# Start chat session
curl "http://localhost:8000/api/v1/ai/chat?language=marathi"

# Send message
curl -X POST http://localhost:8000/api/v1/ai/chat/send \
  -H "Content-Type: application/json" \
  -d '{"session_id": "abc123", "message": "Find best price for iPhone 15", "language": "marathi"}'
```

**Response:** Returns AI-generated response with product recommendations.

### 6. Get Monetization Stats

```bash
curl "http://localhost:8000/api/v1/monetization/stats?days=7"
```

**Response:** Returns revenue, clicks, conversions, and forecasts.

---

## Scrapers

VGAS Shopping AI includes scrapers for:

### India
- ✅ Amazon.in
- ✅ Flipkart.com
- ✅ Myntra.com
- ✅ Ajio.com
- ✅ Tata Cliq
- ✅ Croma
- ✅ Nykaa
- ✅ Reliance Digital

### Global
- ✅ Amazon.com (USA)
- ✅ Amazon.co.uk (UK)
- ✅ Amazon.de (Germany)
- ✅ Amazon.jp (Japan)
- ✅ Amazon.ae (UAE)
- ✅ Walmart.com (USA)
- ✅ eBay.com
- ✅ AliExpress
- ✅ Noon (UAE)

### Features
- **Direct Product Name Search**: Search by typing product names
- **Price Extraction**: Current price, original price, discount percentage
- **Fake Discount Detection**: AI-powered analysis of price history
- **Image Extraction**: Product images for display
- **Rating Extraction**: Customer ratings and reviews
- **Stock Status**: In-stock, out-of-stock, pre-order
- **Specifications**: Detailed product specifications
- **Affiliate Link Generation**: Automatic conversion to earning links

---

## AI Assistant

### Features
- **Multi-Language Support**: Responds in Marathi, Hindi, English, and 20+ languages
- **Intent Detection**: Understands search, compare, discount check, price tracking, etc.
- **Product Recommendations**: Suggests best products based on budget and preferences
- **Fake Discount Alerts**: Warns users about artificial price increases
- **Price Comparison**: Compares prices across multiple stores
- **Translation**: Translates shopping terms between languages
- **Conversation History**: Maintains context across multiple messages

### Example Commands
- "Find the best price for iPhone 15"
- "Compare Samsung Galaxy S24 vs iPhone 15"
- "Is the discount on this URL real?"
- "Alert me when TV price drops below ₹50000"
- "Recommend the best laptop under ₹60000"
- "How can I earn money with VGAS?"

---

## Monetization

VGAS Shopping AI generates revenue through multiple streams:

### 1. Affiliate Marketing (Primary Source)
- **Amazon Associates**: 4-10% commission on purchases
- **Flipkart Affiliate**: 5-10% commission
- **Myntra**: 6-12% commission
- **EarnKaro**: Multi-store affiliate network
- **Cuelinks**: Alternative affiliate network

### 2. Advertising
- **Google AdMob**: Mobile app ads
- **Google AdSense**: Web ads
- **Native Ads**: Custom branded advertisements

### 3. VIP Membership
- **Monthly**: ₹99/month
- **Yearly**: ₹990/year (17% discount)
- **Lifetime**: ₹5000 (one-time payment)
- **US**: $1.99/month

### 4. Sponsorships
- **Brand Partnerships**: Sponsored product listings
- **Featured Deals**: Promoted deals on homepage
- **Content Marketing**: Sponsored blog posts and reviews

### 5. Referral Program
- **5% Override Commission**: Earn on all purchases made through your referral links
- **Multi-level**: Earn from your referrals' referrals
- **Lifetime Earnings**: Continued commission as long as users shop through your links

### Earnings Potential

| User Base | Estimated Monthly Earnings |
|-----------|---------------------------|
| 1,000 users | ₹30,000 - ₹50,000 |
| 5,000 users | ₹1,50,000 - ₹2,50,000 |
| 10,000 users | ₹3,00,000 - ₹5,00,000 |
| 50,000 users | ₹15,00,000 - ₹25,00,000 |
| 100,000 users | ₹30,00,000 - ₹50,00,000 |

### Payout Information
- **Affiliate Commissions**: Net 30-60 days (depends on network)
- **Ad Revenue**: Net 21 days (Google AdMob)
- **Membership Fees**: Immediate (Razorpay)
- **Minimum Payout**: ₹500 for Indian networks, $10 for international
- **Payment Methods**: PayPal, Bank Transfer, UPI

---

## WhatsApp Bot

### Features
- **Direct Product Search**: Users can type product names
- **Price Comparison**: Compare multiple products
- **Fake Discount Detection**: Check if discounts are real
- **Price Alerts**: Set alerts for price drops
- **Deal Notifications**: Get daily loot deals
- **Multi-Language**: Supports Marathi, Hindi, English
- **Broadcast Messages**: Send deals to all users

### Commands
- `Find [product]` - Search for a product
- `Compare [product1] vs [product2]` - Compare products
- `Price [URL]` - Check price and discount
- `Track [URL] for ₹[price]` - Set price alert
- `Deals` - Get today's best deals
- `Earn` - Learn about earning money
- `Help` - Show all commands

### Setup

1. **Install Node.js** (for WhatsApp bot)
2. **Install dependencies**:
   ```bash
   cd D:/Sam/VGAS_Project/bot
   npm install baileys qrcode axios
   ```
3. **Create bot.js** (see WhatsApp bot section below)
4. **Run bot**:
   ```bash
   node bot.js
   ```
5. **Scan QR Code**: Scan the QR code with your WhatsApp mobile app

### WhatsApp Bot Code (bot.js)

```javascript
// VGAS WhatsApp Bot - Node.js with Baileys
const { useSingleFileAuthState, makeWASocket, DisconnectReason, fetchLatestBaileysVersion } = require('@adiwajshing/baileys');
const { Boom } = require('@hapi/boom');
const qrcode = require('qrcode');
const axios = require('axios');
const fs = require('fs');
const path = require('path');

// Configuration
const config = {
    name: 'VGAS Shopping AI Bot',
    phone: process.env.WHATSAPP_PHONE_NUMBER || '919881300933',
    backendUrl: 'http://localhost:8000',
    adminNumbers: ['919881300933'] // Vikas Gunjal's number
};

// Auth state
const authFile = path.join(__dirname, '.auth_info.json');
const { state, saveState } = useSingleFileAuthState(authFile);

// Create socket
async function createSocket() {
    const { version, isLatest } = await fetchLatestBaileysVersion();
    console.log(`Using WA v${version.join('.')}, isLatest: ${isLatest}`);
    
    const sock = makeWASocket({
        version,
        printQRInTerminal: false,
        auth: state,
        browser: ['VGAS Bot', 'Chrome', '1.0.0']
    });
    
    // Save auth state
    sock.ev.on('creds.update', saveState);
    
    // Connection updates
    sock.ev.on('connection.update', (update) => {
        const { connection, lastDisconnect, qr } = update;
        
        if (qr) {
            // Generate QR code
            qrcode.toString(qr, { type: 'terminal' }, (err, url) => {
                if (err) throw err;
                console.log('\nQR CODE FOR WHATSAPP BOT:');
                console.log(url);
            });
        }
        
        if (connection === 'close') {
            const shouldReconnect = (lastDisconnect.error instanceof Boom)?.output?.statusCode !== DisconnectReason.loggedOut;
            console.log('Connection closed due to ', lastDisconnect.error, ', reconnecting ', shouldReconnect);
            if (shouldReconnect) {
                createSocket();
            }
        } else if (connection === 'open') {
            console.log('✅ WhatsApp Bot connected successfully!');
        }
    });
    
    // Message handling
    sock.ev.on('messages.upsert', async (m) => {
        const message = m.messages[0];
        
        if (!message.key.fromMe && m.type === 'notify') {
            const chatId = message.pushName || message.key.remoteJid;
            const from = message.key.remoteJid;
            const body = message.message?.conversation || 
                        message.message?.extendedTextMessage?.text || 
                        message.message?.imageMessage?.caption || 
                        '';
            
            console.log(`\nMessage from ${from}: ${body}`);
            
            try {
                // Process message
                const response = await processMessage(body, from, sock);
                
                // Send response
                await sock.sendMessage(from, {
                    text: response.response || 'Sorry, I could not understand your request.'
                });
                
                // Send additional data if present
                if (response.data && response.data.results) {
                    const results = response.data.results.slice(0, 3);
                    let resultText = '\n📊 *Top Results:*\n\n';
                    results.forEach((result, i) => {
                        resultText += `${i + 1}. *${result.name}*\n`;
                        resultText += `   Price: *₹${result.price?.toLocaleString('en-IN')}*\n`;
                        resultText += `   Store: ${result.store}\n`;
                        resultText += `   Discount: ${result.discount_percentage || 0}%\n`;
                        resultText += `   Link: ${result.url}\n\n`;
                    });
                    resultText += `💡 *Best Price: ₹${response.data.best_price?.toLocaleString('en-IN')} at ${response.data.best_store}*`;
                    
                    await sock.sendMessage(from, { text: resultText });
                }
                
            } catch (error) {
                console.error('Error processing message:', error);
                await sock.sendMessage(from, { 
                    text: '❌ Sorry, I encountered an error processing your request. Please try again.' 
                });
            }
        }
    });
    
    return sock;
}

// Process incoming messages
async function processMessage(message, from, sock) {
    const messageText = message.trim().toLowerCase();
    
    // Greetings
    if (messageText.match(/^(hi|hello|hey|namaste|namaskar|good morning|good afternoon|good evening)$/i)) {
        return {
            response: `👋 Hello! I'm VGAS Shopping AI Bot.\n\nI can help you:
• Find the best prices for any product
• Compare products across stores
• Detect fake discounts
• Set price alerts
• Get daily deals\n\nType "Help" for all commands.`,
            type: 'text'
        };
    }
    
    // Help
    if (messageText.match(/^(help|\?|what can you do|commands)$/i)) {
        return {
            response: `📋 *VGAS Shopping AI Bot Commands:*\n\n` +
                `✅ "Find [product]" - Search for a product\n` +
                `✅ "Compare [product1] vs [product2]" - Compare products\n` +
                `✅ "Price [URL]" - Check product price\n` +
                `✅ "Track [URL] for ₹[price]" - Set price alert\n` +
                `✅ "Deals" - Get today's best deals\n` +
                `✅ "Earn" - Learn about earning money\n` +
                `✅ "Help" - Show this help\n\n` +
                `💡 *Example: Find iPhone 15*`,
            type: 'text'
        };
    }
    
    // Search for products
    if (messageText.startsWith('find ') || messageText.startsWith('search ') || messageText.startsWith('show ') || messageText.includes(' best price')) {
        const productName = messageText.replace(/^(find|search|show|best price|get|i want|i need)/i, '').trim();
        
        if (productName) {
            try {
                // Call backend API
                const response = await axios.get(`${config.backendUrl}/api/v1/search/`, {
                    params: {
                        query: productName,
                        country: 'India',
                        limit: 5,
                        sort_by: 'price_asc'
                    }
                });
                
                return {
                    response: `🔍 Found ${response.data.total_results} results for "${productName}":`,
                    data: response.data
                };
            } catch (error) {
                console.error('Search error:', error);
                return {
                    response: `❌ Sorry, I couldn't find any results for "${productName}". Please try a different search term.`
                };
            }
        }
    }
    
    // Compare products
    if (messageText.startsWith('compare ') || messageText.includes(' vs ') || messageText.includes(' versus ')) {
        const products = messageText.replace(/^compare/i, '').split(/ vs | versus /i);
        
        if (products.length >= 2) {
            return {
                response: `📊 I'll compare these products for you: ${products.join(', ')}...\n\nPlease wait while I fetch the latest prices and features.`,
                data: { products }
            };
        }
    }
    
    // Get deals
    if (messageText.match(/^(deals|loot deals|offers|discounts|today's deals)$/i)) {
        try {
            const response = await axios.get(`${config.backendUrl}/api/v1/search/loot-deals?limit=5`);
            
            return {
                response: `🔥 *Today's Loot Deals (80-90% OFF)*\n\nFound ${response.data.length} amazing deals!`,
                data: { results: response.data }
            };
        } catch (error) {
            return {
                response: '❌ Sorry, I couldn\'t fetch the deals. Please try again later.'
            };
        }
    }
    
    // Earn money
    if (messageText.match(/^(earn|money|affiliate|commission|how to earn|referral)$/i)) {
        return {
            response: `💰 *Earn Money with VGAS Shopping AI!*\n\n` +
                `Share VGAS links with your friends and earn 2-10% commission on every purchase they make!\n\n` +
                `Your PayPal: ${config.phone === '919881300933' ? 'gunjalvikas786@gmail.com' : 'Configured'}\n\n` +
                `Supported Stores:\n` +
                `✅ Amazon (4-10%)\n` +
                `✅ Flipkart (5-10%)\n` +
                `✅ Myntra (6-12%)\n` +
                `✅ Ajio (5-10%)\n\n` +
                `Earnings Potential: ₹10,000 - ₹1,00,000+/month`
        };
    }
    
    // Price check
    if (messageText.startsWith('price ') || messageText.startsWith('check ')) {
        const url = messageText.replace(/^(price|check)/i, '').trim();
        
        if (url) {
            try {
                const response = await axios.get(`${config.backendUrl}/api/v1/products/by-url?url=${encodeURIComponent(url)}`);
                const data = response.data;
                
                return {
                    response: `🏷️ *Product Details:*\n\n` +
                        `Name: *${data.name || 'N/A'}*\n` +
                        `Price: *₹${data.current_price?.toLocaleString('en-IN') || 'N/A'}*\n` +
                        `Original: ~~₹${data.original_price?.toLocaleString('en-IN') || 'N/A'}~~\n` +
                        `Discount: *${data.discount_percentage || 0}% OFF*\n` +
                        `Rating: ${data.rating || 0}/5\n` +
                        `Store: ${data.store || 'N/A'}\n` +
                        `${data.is_fake_discount ? '⚠️ *FAKE DISCOUNT DETECTED!*\n' : ''}` +
                        `${data.fake_discount_recommendation || ''}`
                };
            } catch (error) {
                return {
                    response: `❌ Sorry, I couldn't check the price for that URL. Please make sure it's a valid product link from a supported store.`
                };
            }
        }
    }
    
    // Default response
    return {
        response: `I'm VGAS Shopping AI Bot! 🛒\n\nI can help you find the best prices, compare products, detect fake discounts, and more.\n\nType "Help" to see all available commands.`
    };
}

// Start the bot
createSocket().catch(err => console.log('Error starting bot:', err));

// Handle process termination
process.on('SIGINT', () => {
    console.log('\n👋 WhatsApp Bot stopped');
    process.exit(0);
});
```

---

## Frontend Integration

### Android App (Existing)

The existing Android app in `shopping-ai/` folder can be connected to this backend by:

1. **Update API Base URL**:
   ```kotlin
   // In your Android app's API client
   const val BASE_URL = 