"""
Telegram Bot Integration for GoGrabit

Set these environment variables:
- TELEGRAM_BOT_TOKEN: Your bot token from @BotFather
- TELEGRAM_CHAT_ID: Chat ID where notifications will be sent
"""

import os
import asyncio
from telegram import Bot, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.error import TelegramError


# Get configuration from environment
BOT_TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN', '')
CHAT_ID = os.environ.get('TELEGRAM_CHAT_ID', '')

# Initialize bot
bot = None
if BOT_TOKEN:
    bot = Bot(token=BOT_TOKEN)


def send_order_notification(order):
    """Send new order notification with action button"""
    if not bot or not CHAT_ID:
        print("Telegram bot not configured")
        return
    
    try:
        # Format message
        items_text = '\n'.join([
            f"  • {item['name']} x{item['qty']} - ₹{item['price'] * item['qty']}"
            for item in order.items
        ])
        
        message = f"""
🆕 <b>New Order: {order.order_id}</b>

👤 Customer: {order.customer_name}
📱 Phone: {order.phone_number}
🏠 Room: {order.room_number}

📦 <b>Items:</b>
{items_text}

💰 <b>Total: ₹{order.total_amount}</b>

⏰ Expires: {order.expires_at.strftime('%H:%M:%S')}
"""
        
        # Create inline keyboard with "Mark as Picked" button
        keyboard = [
            [InlineKeyboardButton("✅ Mark as Picked", callback_data=f"pick_{order.order_id}")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        # Send message asynchronously
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        message_obj = loop.run_until_complete(
            bot.send_message(
                chat_id=CHAT_ID,
                text=message,
                parse_mode='HTML',
                reply_markup=reply_markup
            )
        )
        loop.close()
        
        # Store message ID for later editing
        order.telegram_message_id = message_obj.message_id
        order.save()
        
        print(f"Telegram notification sent for order {order.order_id}")
        
    except TelegramError as e:
        print(f"Telegram error: {e}")
    except Exception as e:
        print(f"Error sending Telegram notification: {e}")


def send_order_picked_notification(order):
    """Send notification when order is picked"""
    if not bot or not CHAT_ID:
        return
    
    try:
        message = f"""
✅ <b>Order Picked: {order.order_id}</b>

👤 {order.customer_name}
🏠 Room {order.room_number}
💰 ₹{order.total_amount}

Status: <b>PICKED - Ready for payment</b>
"""
        
        # Send new message
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(
            bot.send_message(
                chat_id=CHAT_ID,
                text=message,
                parse_mode='HTML'
            )
        )
        loop.close()
        
        # Edit original message if exists
        if order.telegram_message_id:
            edit_message(CHAT_ID, order.telegram_message_id, f"✅ Order {order.order_id} - <b>PICKED</b>")
        
    except Exception as e:
        print(f"Error sending picked notification: {e}")


def answer_callback_query(callback_query_id, text):
    """Answer callback query from button press"""
    if not bot:
        return
    
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(
            bot.answer_callback_query(callback_query_id=callback_query_id, text=text)
        )
        loop.close()
    except Exception as e:
        print(f"Error answering callback: {e}")


def edit_message(chat_id, message_id, text):
    """Edit existing message"""
    if not bot:
        return
    
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(
            bot.edit_message_text(
                chat_id=chat_id,
                message_id=message_id,
                text=text,
                parse_mode='HTML'
            )
        )
        loop.close()
    except Exception as e:
        print(f"Error editing message: {e}")


def send_low_stock_alert(product):
    """Send low stock alert"""
    if not bot or not CHAT_ID:
        return
    
    try:
        message = f"""
⚠️ <b>Low Stock Alert</b>

Product: {product.name}
Category: {product.category}
Current Stock: <b>{product.stock}</b>

Please restock soon!
"""
        
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(
            bot.send_message(
                chat_id=CHAT_ID,
                text=message,
                parse_mode='HTML'
            )
        )
        loop.close()
        
    except Exception as e:
        print(f"Error sending stock alert: {e}")
