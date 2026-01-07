import os
import asyncio
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters
from app.core.config import settings
from app.core.database import SessionLocal
from app.models.transaction import Transaction
from pathlib import Path
from datetime import date

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Store temporary data
user_data_store = {}


def is_authorized(user_id: int) -> bool:
    """Check if user is authorized"""
    allowed_users = settings.get_allowed_telegram_users()
    return user_id in allowed_users if allowed_users else True


async def start(update: Update, context):
    """Handle /start command"""
    if not is_authorized(update.effective_user.id):
        await update.message.reply_text("⛔️ Du bist nicht autorisiert, diesen Bot zu verwenden.")
        return
    
    await update.message.reply_text(
        "💰 Willkommen beim Money Manager Bot!\n\n"
        "Sende mir:\n"
        "📄 PDF/Foto einer Rechnung\n"
        "💬 /pending - Zeige offene Buchungen\n"
        "📊 /accounts - Zeige Konten\n"
    )


async def handle_document(update: Update, context):
    """Handle document uploads (receipts)"""
    if not is_authorized(update.effective_user.id):
        return
    
    user_id = update.effective_user.id
    message = update.message
    
    # Download file
    file = await message.document.get_file()
    
    # Create temporary directory
    temp_dir = Path(settings.RECEIPTS_PATH) / "pending"
    temp_dir.mkdir(parents=True, exist_ok=True)
    
    file_path = temp_dir / f"{file.file_id}.pdf"
    await file.download_to_drive(file_path)
    
    # Try OCR extraction (basic implementation)
    extracted_data = extract_receipt_data(str(file_path))
    
    # Create pending transaction
    db = SessionLocal()
    try:
        transaction = Transaction(
            account_id=1,  # Default account, user can change
            date=extracted_data.get("date", date.today()),
            amount=extracted_data.get("amount", 0.00),
            description=extracted_data.get("description", "Neue Rechnung"),
            status="pending",
            source="telegram",
            requires_confirmation=True,  # Automatisch = Bestätigung erforderlich
            receipt_path=str(file_path),
            telegram_message_id=message.message_id
        )
        db.add(transaction)
        db.commit()
        db.refresh(transaction)
        
        # Store in temporary data
        user_data_store[user_id] = {
            "transaction_id": transaction.id,
            "file_path": str(file_path)
        }
        
        # Send confirmation with buttons
        keyboard = [
            [
                InlineKeyboardButton("✅ Bestätigen", callback_data=f"confirm_{transaction.id}"),
                InlineKeyboardButton("✏️ Bearbeiten", callback_data=f"edit_{transaction.id}")
            ],
            [
                InlineKeyboardButton("🗑 Löschen", callback_data=f"delete_{transaction.id}")
            ]
        ]
        
        await message.reply_text(
            f"📄 Rechnung empfangen!\n\n"
            f"💰 Betrag: CHF {extracted_data.get('amount', 0.00):.2f}\n"
            f"📅 Datum: {extracted_data.get('date', date.today())}\n"
            f"📝 Beschreibung: {extracted_data.get('description', 'Keine')}\n\n"
            f"Status: Provisorisch gespeichert",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
        
    finally:
        db.close()


async def handle_photo(update: Update, context):
    """Handle photo uploads"""
    if not is_authorized(update.effective_user.id):
        return
    
    # Similar to handle_document but for photos
    photo = update.message.photo[-1]  # Get highest resolution
    file = await photo.get_file()
    
    temp_dir = Path(settings.RECEIPTS_PATH) / "pending"
    temp_dir.mkdir(parents=True, exist_ok=True)
    
    file_path = temp_dir / f"{file.file_id}.jpg"
    await file.download_to_drive(file_path)
    
    extracted_data = extract_receipt_data(str(file_path))
    
    db = SessionLocal()
    try:
        transaction = Transaction(
            account_id=1,
            date=extracted_data.get("date", date.today()),
            amount=extracted_data.get("amount", 0.00),
            description=extracted_data.get("description", "Foto Rechnung"),
            status="pending",
            source="telegram",
            requires_confirmation=True,  # Automatisch = Bestätigung erforderlich
            receipt_path=str(file_path),
            telegram_message_id=update.message.message_id
        )
        db.add(transaction)
        db.commit()
        db.refresh(transaction)
        
        keyboard = [
            [
                InlineKeyboardButton("✅ Bestätigen", callback_data=f"confirm_{transaction.id}"),
                InlineKeyboardButton("✏️ Bearbeiten", callback_data=f"edit_{transaction.id}")
            ],
            [InlineKeyboardButton("🗑 Löschen", callback_data=f"delete_{transaction.id}")]
        ]
        
        await update.message.reply_text(
            f"📸 Foto empfangen!\n\n"
            f"💰 Betrag: CHF {extracted_data.get('amount', 0.00):.2f}\n"
            f"📅 Datum: {extracted_data.get('date', date.today())}\n"
            f"📝 Beschreibung: {extracted_data.get('description', 'Keine')}\n\n"
            f"Status: Provisorisch gespeichert",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
    finally:
        db.close()


async def button_callback(update: Update, context):
    """Handle button callbacks"""
    query = update.callback_query
    await query.answer()
    
    action, transaction_id = query.data.split("_")
    transaction_id = int(transaction_id)
    
    db = SessionLocal()
    try:
        transaction = db.query(Transaction).filter(Transaction.id == transaction_id).first()
        
        if not transaction:
            await query.edit_message_text("❌ Transaktion nicht gefunden.")
            return
        
        if action == "confirm":
            transaction.status = "confirmed"
            db.commit()
            await query.edit_message_text(
                f"✅ Transaktion bestätigt!\n\n"
                f"💰 CHF {transaction.amount:.2f}\n"
                f"📝 {transaction.description}"
            )
        
        elif action == "delete":
            # Delete file if exists
            if transaction.receipt_path and os.path.exists(transaction.receipt_path):
                os.remove(transaction.receipt_path)
            db.delete(transaction)
            db.commit()
            await query.edit_message_text("🗑 Transaktion gelöscht.")
        
        elif action == "edit":
            await query.edit_message_text(
                f"✏️ Bearbeiten:\n\n"
                f"Aktuelle Daten:\n"
                f"💰 Betrag: CHF {transaction.amount:.2f}\n"
                f"📝 Beschreibung: {transaction.description}\n\n"
                f"Bitte verwende die Web-App um zu bearbeiten:\n"
                f"http://localhost:3000/transactions/{transaction.id}"
            )
    
    finally:
        db.close()


async def pending_transactions(update: Update, context):
    """Show pending transactions"""
    if not is_authorized(update.effective_user.id):
        return
    
    db = SessionLocal()
    try:
        pending = db.query(Transaction).filter(Transaction.status == "pending").all()
        
        if not pending:
            await update.message.reply_text("✅ Keine offenen Buchungen.")
            return
        
        message = "📋 Offene Buchungen:\n\n"
        for tx in pending:
            message += f"💰 CHF {tx.amount:.2f} - {tx.description}\n"
            message += f"📅 {tx.date}\n\n"
        
        await update.message.reply_text(message)
    
    finally:
        db.close()


def extract_receipt_data(file_path: str) -> dict:
    """Extract data from receipt using OCR (basic implementation)"""
    # TODO: Implement proper OCR with Tesseract or other service
    # For now, return dummy data
    
    return {
        "amount": 0.00,
        "date": date.today(),
        "description": "Neue Rechnung (OCR nicht implementiert)"
    }


def main():
    """Start the bot"""
    if not settings.TELEGRAM_BOT_TOKEN:
        logger.error("TELEGRAM_BOT_TOKEN not set!")
        return
    
    application = Application.builder().token(settings.TELEGRAM_BOT_TOKEN).build()
    
    # Add handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("pending", pending_transactions))
    application.add_handler(MessageHandler(filters.Document.ALL, handle_document))
    application.add_handler(MessageHandler(filters.PHOTO, handle_photo))
    application.add_handler(CallbackQueryHandler(button_callback))
    
    # Start bot
    logger.info("Starting Money Manager Telegram Bot...")
    application.run_polling()


if __name__ == "__main__":
    main()
