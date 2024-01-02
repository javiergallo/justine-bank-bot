import logging

from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
    MessageHandler,
)

from ormar.exceptions import AsyncOrmException

from justine_bank.models import Issue, Transfer, Wallet
from justine_bank.settings import config


ERROR_TEXT_PATTERN = "Uy! Algo salió mal! {description} \U0001F974"
WELCOME_TEXT_PATTERN = (
    "¡Hola @{username}! Soy el bot administrador del Banco de Justines. Enviá "
    "/help si querés que te cuente qué se puede hacer en el Banco de Justines."
)
WALLET_TEXT_PATTERN = "@{username}: {balance} justines"
ISSUE_TEXT_PATTERN = "{amount} justines emitidos a @{recipient_username}"
TRANSFER_TEXT_PATTERN = (
    "{amount} justines transferidos de @{sender_username} a "
    "@{recipient_username}"
)

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
        reply_text += "/list_issues - listar emisiones realizadas.\n"
        reply_text += "/issue [amount] [username] - emitir justines a un usuario.\n"
        reply_text += "/list_transfers - listar transferencias realizadas.\n"
    reply_text += "/transfer [amount] [username] - transferir justines a un usuario.\n"

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
    try:
        amount_str, recipient_username = context.args
        amount = float(amount_str)
        
        recipient, _ = await Wallet.objects.get_or_create(
            owner_username=recipient_username
        )
        issue = Issue(recipient=recipient, amount=amount)

        await recipient.update(balance=recipient.balance + amount)
        await issue.save()

    except (ValueError, AsyncOrmException) as exception:
        reply_text = ERROR_TEXT_PATTERN.format(
            description=(
                "No se pudieron emitir los justines. Por favor, revisá la "
                "lista de parámetros y los valores que ingresaste."
            )
        )
        logger.exception(
            f"Something went wrong while issuing justines: {exception}."
        )

    else:
        reply_text = ISSUE_TEXT_PATTERN.format(
            amount=amount,
            recipient_username=recipient_username,
        )
        logger.info(f"{amount} justines issued to {recipient_username}")

    await update.message.reply_text(reply_text)
    


async def list_transfers(update: Update, context: ContextTypes.DEFAULT_TYPE):
    transfers = (
        await Transfer.objects.select_related(["sender", "recipient"]).all()
    )
    reply_text = "\n".join(
        TRANSFER_TEXT_PATTERN.format(
            amount=transfer.amount,
            sender_username=transfer.sender.owner_username,
            recipient_username=transfer.recipient.owner_username,
        )
        for transfer in transfers
    )

    await update.message.reply_text(reply_text)
    logger.info("Transfers listed")


async def transfer(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        sender_username = update.message.from_user.username
        amount_str, recipient_username = context.args
        amount = float(amount_str)

        sender, _ = await Wallet.objects.get_or_create(
            owner_username=sender_username
        )
        recipient, _ = await Wallet.objects.get_or_create(
            owner_username=recipient_username
        )
        transfer = Transfer(sender=sender, recipient=recipient, amount=amount)

        await sender.update(balance=sender.balance - amount)
        await recipient.update(balance=recipient.balance + amount)
        await transfer.save()

    except (ValueError, AsyncOrmException) as exception:
        reply_text = ERROR_TEXT_PATTERN.format(
            description=(
                "No se pudieron transferir los justines. Por favor, revisá la "
                "lista de parámetros y los valores que ingresaste."
            )
        )
        logger.exception(
            f"Something went wrong while transferring justines: {exception}."
        )

    else:
        reply_text = TRANSFER_TEXT_PATTERN.format(
            amount=amount,
            sender_username=sender_username,
            recipient_username=recipient_username,
        )
        logger.info(
            f"{amount} justines transferred from {sender_username} to "
            f"{recipient_username}"
        )

    await update.message.reply_text(reply_text)


if __name__ == "__main__":
    app = Application.builder().token(config.api_token).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help))
    app.add_handler(CommandHandler("list_wallets", list_wallets))
    app.add_handler(CommandHandler("list_issues", list_issues))
    app.add_handler(CommandHandler("issue", issue))
    app.add_handler(CommandHandler("list_transfers", list_transfers))
    app.add_handler(CommandHandler("transfer", transfer))

    logger.info("Polling...")
    app.run_polling(poll_interval=config.poll_interval)
