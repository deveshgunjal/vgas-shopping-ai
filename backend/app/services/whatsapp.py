"""WhatsApp Bot Integration via Twilio"""
from fastapi import APIRouter, Request, Form
from fastapi.responses import PlainTextResponse
import re
import httpx
import os

router = APIRouter()

TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID", "")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN", "")
TWILIO_WHATSAPP_NUMBER = os.getenv("TWILIO_WHATSAPP_NUMBER", "whatsapp:+14155238886")

@router.post("/api/v1/whatsapp/webhook")
async def whatsapp_webhook(
    Body: str = Form(""),
    From: str = Form(""),
    MediaUrl0: str = Form(None),
):
    """Handle incoming WhatsApp messages"""
    user_message = Body.strip()
    
    # Extract URL from message
    url_match = re.search(r'https?://[^\s]+', user_message)
    
    if url_match:
        url = url_match.group(0)
        from ..scrapers.crawler import crawler
        
        result = await crawler.crawl(url)
        
        if result.get("price"):
            response = f"Price Found!\n\n"
            response += f"{result.get('title', 'Product')}\n"
            response += f"Price: INR {result['price']}\n"
            response += f"Store: {result.get('store', 'Unknown')}\n"
            response += f"\nSend another URL to compare!"
        else:
            response = "Could not find price. Try another URL."
    elif MediaUrl0:
        response = "Image received! AI Vision processing coming soon.\nSend a product URL for instant price check."
    else:
        response = "Welcome to Vgas Shopping AI!\n\n"
        response += "Send me a product URL and I will find the lowest price!\n\n"
        response += "Commands:\n"
        response += "/deals - Today best deals\n"
        response += "/track - Track a product\n"
        response += "/help - Show this message"
    
    twiml = f"""<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Message>{response}</Message>
</Response>"""
    
    return PlainTextResponse(twiml, media_type="application/xml")
