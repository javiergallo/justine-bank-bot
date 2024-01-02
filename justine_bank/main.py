import logging

from telegram import Update
from telegram.ext import Application, ContextTypes

from ormar.exceptions import AsyncOrmException

from justine_bank.commands import Menu
from justine_bank.constants import (
    ERROR_TEXT_PATTERN,
    ISSUE_TEXT_PATTERN,
    START_TEXT_PATTERN,
    TRANSFER_TEXT_PATTERN,
    WALLET_TEXT_PATTERN,
)
from justine_bank.models import Issue, Transfer, Wallet
from justine_bank.settings import config
from justine_bank.utils import clean_username

logging.basicConfig(
    format='%(asctime)s %(levelname)-8s %(message)s',
    level=logging.INFO,
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger('abc')

menu = Menu()


@menu.command(
    "start",
    help_text="Iniciar/reiniciar nuestra conversación (nada sorprendente)"
)
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    username = update.message.from_user.username
    reply_text = START_TEXT_PATTERN.format(username=username)
    await update.message.reply_text(reply_text)
    logger.info("App started")


@menu.command(
    "help",
    help_text="Mostrar la ayuda (i.e., esta lista de comandos)"
)
async def help(update: Update, context: ContextTypes.DEFAULT_TYPE):
    username = update.message.from_user.username

    reply_text = ""
    for statement in menu:
        if not statement.exclusive or username in config.staff_usernames:
            cmd_name = next(iter(statement.handler.commands))
            arg_names_str = ' '.join(f"[{name}]" for name in statement.arg_names)
            reply_text += f"/{cmd_name} {arg_names_str} - {statement.help_text}\n"

    await update.message.reply_text(reply_text)
    logger.info("Help replied")


@menu.command(
    "listwallets",
    help_text="Listar billeteras"
)
async def list_wallets(update: Update, context: ContextTypes.DEFAULT_TYPE):
    username = update.message.from_user.username

    if username in config.staff_usernames:
        wallets = await Wallet.objects.all()
    else:
        wallets = await Wallet.objects.filter(owner_username=username).all()

    reply_text = "\n".join(
        WALLET_TEXT_PATTERN.format(wallet=wallet)
        for wallet in wallets
    )

    await update.message.reply_text(reply_text)
    logger.info("Wallets listed")


@menu.command(
    "listissues",
    help_text="Listar emisiones realizadas",
    exclusive=True
)
async def list_issues(update: Update, context: ContextTypes.DEFAULT_TYPE):
    username = update.message.from_user.username

    if username in config.staff_usernames:
        issues = await Issue.objects.select_related("recipient").all()
        reply_text = "\n".join(
            ISSUE_TEXT_PATTERN.format(issue=issue) for issue in issues
        )

        await update.message.reply_text(reply_text)
        logger.info("Issues listed")


@menu.command(
    "issue",
    arg_names=("amount", "username"),
    help_text="Emitir justines a un usuario",
    exclusive=True
)
async def issue(update: Update, context: ContextTypes.DEFAULT_TYPE):
    username = update.message.from_user.username

    if username in config.staff_usernames:
        try:
            amount = float(context.args[0])
            recipient_username = clean_username(context.args[1])
            
            recipient, _ = await Wallet.objects.get_or_create(
                owner_username=recipient_username
            )
            issue = Issue(recipient=recipient, amount=amount)

            await recipient.update(balance=recipient.balance + amount)
            await issue.save()

        except (IndexError, ValueError, AsyncOrmException) as exception:
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
            reply_text = ISSUE_TEXT_PATTERN.format(issue=issue)
            logger.info(f"{amount} justines issued to {recipient_username}")

        await update.message.reply_text(reply_text)


@menu.command(
    "listtransfers",
    help_text="Listar transferencias realizadas"
)
async def list_transfers(update: Update, context: ContextTypes.DEFAULT_TYPE):
    username = update.message.from_user.username

    if username in config.staff_usernames:
        transfers = (
            await Transfer.objects.select_related(["sender", "recipient"]).all()
        )
    else:
        transfers = (
            await Transfer.objects.select_related(["sender", "recipient"]).filter(
                sender__owner_username=username
            ).all()
        )

    reply_text = "\n".join(
        TRANSFER_TEXT_PATTERN.format(transfer=transfer)
        for transfer in transfers
    )

    await update.message.reply_text(reply_text)
    logger.info("Transfers listed")


@menu.command(
    "transfer",
    arg_names=("amount", "username"),
    help_text="Transferir justines a un usuario"
)
async def transfer(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        sender_username = update.message.from_user.username
        amount = float(context.args[0])
        recipient_username = clean_username(context.args[1])

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

    except (IndexError, ValueError, AsyncOrmException) as exception:
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
        reply_text = TRANSFER_TEXT_PATTERN.format(transfer=transfer)
        logger.info(
            f"{amount} justines transferred from {sender_username} to "
            f"{recipient_username}"
        )

    await update.message.reply_text(reply_text)


if __name__ == "__main__":
    app = Application.builder().token(config.api_token).build()

    for statement in menu:
        app.add_handler(statement.handler)

    logger.info("Polling...")
    app.run_polling(poll_interval=config.poll_interval)
