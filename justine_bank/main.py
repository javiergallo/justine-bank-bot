import logging

from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
    MessageHandler,
)

from justine_bank.models import Issue, Transfer, Wallet

API_TOKEN = "6781101095:AAEYSlIPOQ4SDdn3zDxYs0UhtIwMZPIiHwg"
USERNAME = "JustineBankBot"

WELCOME_TEXT_PATTERN = (
    "¡Hola {username}! Soy el bot administrador del Banco de Justines. Enviá "
    "/help si querés que te cuente qué se puede hacer en el Banco de Justines."
)
WALLET_TEXT_PATTERN = "{username}: {balance} justines"
ISSUE_TEXT_PATTERN = "{amount} justines emitidos a {recipient_username}"

POLL_INTERVAL = 3

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('abc')


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    username = update.message.from_user.username
    reply_text = WELCOME_TEXT_PATTERN.format(username=username)
    await update.message.reply_text(reply_text)
    logger.info("App started")


async def help(update: Update, context: ContextTypes.DEFAULT_TYPE):
    reply_text = ""
    reply_text += "/start - comenzar.\n"
    reply_text += "/help - mostrar esta lista de comandos.\n"
    if update.message.chat.type != "group":
        reply_text += "/list_wallets - listar billeteras.\n"
        reply_text += "/list_issues - listar emisiones.\n"
        reply_text += "/issue [amount][username] - emitir justines a un usuario.\n"
        
    await update.message.reply_text(reply_text)
    logger.info("Help replied")

async def list_wallets(update: Update, context: ContextTypes.DEFAULT_TYPE):
    wallets = await Wallet.objects.all()
    reply_text = "\n".join(
        WALLET_TEXT_PATTERN.format(
            username=wallet.owner_username,
            balance=wallet.balance,
        )
        for wallet in wallets
    )

    await update.message.reply_text(reply_text)
    logger.info("Wallets listed")

async def list_issues(update: Update, context: ContextTypes.DEFAULT_TYPE):
    issues = await Issue.objects.select_related("recipient").all()
    reply_text = "\n".join(
        ISSUE_TEXT_PATTERN.format(
            amount=issue.amount,
            recipient_username=issue.recipient.owner_username,
        )
        for issue in issues
    )

    await update.message.reply_text(reply_text)
    logger.info("Issues listed")

async def issue(update: Update, context: ContextTypes.DEFAULT_TYPE):
    amount_str, recipient_username = context.args
    amount = float(amount_str)

    recipient, _ = await Wallet.objects.get_or_create(
        owner_username=recipient_username
    )
    await recipient.update(balance=recipient.balance + amount)

    issue = Issue(recipient=recipient, amount=amount)
    await issue.save()

    reply_text = ISSUE_TEXT_PATTERN.format(
        amount=amount,
        recipient_username=recipient_username,
    )
    await update.message.reply_text(reply_text)
    logger.info(f"{amount} justines issued to {recipient_username}")


if __name__ == "__main__":
    app = Application.builder().token(API_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help))
    app.add_handler(CommandHandler("list_wallets", list_wallets))
    app.add_handler(CommandHandler("list_issues", list_issues))
    app.add_handler(CommandHandler("issue", issue))

    logger.info("Polling...")
    app.run_polling(poll_interval=POLL_INTERVAL)
