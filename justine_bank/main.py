import logging

import typer

from telegram import Update
from telegram.ext import Application, ContextTypes

from ormar.exceptions import AsyncOrmException

from justine_bank.commands import Menu
from justine_bank.constants import (
    CHARGE_TEXT_PATTERN,
    ERROR_TEXT_PATTERN,
    ISSUE_TEXT_PATTERN,
    NO_ITEMS_TEXT_PATTERN,
    START_TEXT_PATTERN,
    TRANSFER_TEXT_PATTERN,
    WALLET_TEXT_PATTERN,
)
from justine_bank.localization import _
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
    help_text=_("Start or restart this conversation")
)
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    username = update.message.from_user.username
    reply_text = START_TEXT_PATTERN.format(username=username)
    await update.message.reply_text(reply_text)
    logger.info(_("App started"))


@menu.command(
    "help",
    help_text=_("Show help")
)
async def help(update: Update, context: ContextTypes.DEFAULT_TYPE):
    username = clean_username(update.message.from_user.username)

    reply_text = _("List of commands:") + "\n\n"
    for statement in menu:
        if not statement.restricted or username in config.staff_usernames:
            cmd_name = next(iter(statement.handler.commands))
            arg_names_str = ' '.join(f"[{name}]" for name in statement.arg_names)
            reply_text += f"/{cmd_name} {arg_names_str}\n{statement.help_text}\n"
            if statement.example:
                reply_text += _("*For example*:\n{example}\n").format(
                    example=statement.example
                )
            reply_text += "\n"

    await update.message.reply_text(reply_text, parse_mode='Markdown')
    logger.info(_("Help replied"))


@menu.command(
    "listwallets",
    help_text=_("List wallets"),
    restricted=True,
)
async def list_wallets(update: Update, context: ContextTypes.DEFAULT_TYPE):
    username = clean_username(update.message.from_user.username)

    if username in config.staff_usernames:
        wallets = await Wallet.objects.all()

        if wallets:
            reply_text = "\n".join(
                WALLET_TEXT_PATTERN.format(wallet=wallet)
                for wallet in wallets
            )
        else:
            reply_text = NO_ITEMS_TEXT_PATTERN.format(items_type="billeteras")

        await update.message.reply_text(reply_text)
        logger.info(_("Wallets listed"))


@menu.command(
    "showwallet",
    help_text=_("Show wallet"),
)
async def show_wallet(update: Update, context: ContextTypes.DEFAULT_TYPE):
    username = clean_username(update.message.from_user.username)
    wallet, created = await Wallet.objects.get_or_create(
        owner_username=username
    )

    reply_text = WALLET_TEXT_PATTERN.format(wallet=wallet)

    await update.message.reply_text(reply_text)
    logger.info(_("Wallet shown"))


@menu.command(
    "listissues",
    help_text=_("List issues"),
    restricted=True
)
async def list_issues(update: Update, context: ContextTypes.DEFAULT_TYPE):
    username = clean_username(update.message.from_user.username)

    if username in config.staff_usernames:
        issues = await Issue.objects.select_related("recipient").all()

        if issues:
            reply_text = "\n".join(
                ISSUE_TEXT_PATTERN.format(issue=issue) for issue in issues
            )
        else:
            reply_text = NO_ITEMS_TEXT_PATTERN.format(items_type=_("issues"))

        await update.message.reply_text(reply_text)
        logger.info(_("Issues listed"))


@menu.command(
    "issue",
    arg_names=("amount", "username"),
    help_text=_("Issue justines for a user"),
    example=_("`/issue 300 @javier_rooster`"),
    restricted=True
)
async def issue(update: Update, context: ContextTypes.DEFAULT_TYPE):
    username = clean_username(update.message.from_user.username)

    if username in config.staff_usernames:
        try:
            amount = float(context.args[0])
            recipient_username = clean_username(context.args[1])

            recipient, created = await Wallet.objects.get_or_create(
                owner_username=recipient_username
            )
            issue = Issue(recipient=recipient, amount=amount)

            await recipient.update(balance=recipient.balance + amount)
            await issue.save()

        except (IndexError, ValueError, AsyncOrmException) as exception:
            reply_text = ERROR_TEXT_PATTERN.format(
                description=_("Justines couldn't be issued. Review input.")
            )
            logger.exception(
                _("Something went wrong while issuing justines: {exception}.").format(
                    exception=exception
                )
            )

        else:
            reply_text = ISSUE_TEXT_PATTERN.format(issue=issue)
            logger.info(
                _("{amount} justines issued to {recipient_username}").format(
                    amount=amount,
                    recipient_username=recipient_username,
                )
            )

        await update.message.reply_text(reply_text)


@menu.command(
    "listtransfers",
    help_text=_("List transfers")
)
async def list_transfers(update: Update, context: ContextTypes.DEFAULT_TYPE):
    username = clean_username(update.message.from_user.username)

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

    if transfers:
        reply_text = "\n".join(
            TRANSFER_TEXT_PATTERN.format(transfer=transfer)
            for transfer in transfers
        )
    else:
        reply_text = NO_ITEMS_TEXT_PATTERN.format(items_type=_("transfers"))

    await update.message.reply_text(reply_text)
    logger.info(_("Transfers listed"))


@menu.command(
    "transfer",
    arg_names=("amount", "username"),
    help_text=_("Transfer justines to a user"),
    example=_("`/transfer 300 @javier_rooster`"),
)
async def transfer(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        sender_username = clean_username(update.message.from_user.username)
        amount = float(context.args[0])
        recipient_username = clean_username(context.args[1])

        assert sender_username != recipient_username

        sender, created = await Wallet.objects.get_or_create(
            owner_username=sender_username
        )
        recipient, created = await Wallet.objects.get_or_create(
            owner_username=recipient_username
        )
        transfer = Transfer(sender=sender, recipient=recipient, amount=amount)

        await sender.update(balance=sender.balance - amount)
        await recipient.update(balance=recipient.balance + amount)
        await transfer.save()

    except (AssertionError, IndexError, ValueError, AsyncOrmException) as exception:
        reply_text = ERROR_TEXT_PATTERN.format(
            description=_("Justines couldn't be transfered. Review input.")
        )
        logger.exception(
            _("Something went wrong while transferring justines: {exception}.").format(
                exception=exception
            )
        )

    else:
        reply_text = TRANSFER_TEXT_PATTERN.format(transfer=transfer)
        logger.info(
            _("{amount} justines transferred from {sender_username} to {recipient_username}").format(
                amount=amount,
                sender_username=sender_username,
                recipient_username=recipient_username,
            )
        )

    await update.message.reply_text(reply_text)


@menu.command(
    "charge",
    arg_names=("amount", "username"),
    help_text=_("Charge a user"),
    example=_("`/charge 300 @javier_rooster`"),
    restricted=True
)
async def charge(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        sender_username = clean_username(context.args[1])
        amount = float(context.args[0])
        recipient_username = clean_username(update.message.from_user.username)

        assert sender_username != recipient_username

        sender, created = await Wallet.objects.get_or_create(
            owner_username=sender_username
        )
        recipient, created = await Wallet.objects.get_or_create(
            owner_username=recipient_username
        )
        transfer = Transfer(sender=sender, recipient=recipient, amount=amount)

        await sender.update(balance=sender.balance - amount)
        await recipient.update(balance=recipient.balance + amount)
        await transfer.save()

    except (AssertionError, IndexError, ValueError, AsyncOrmException) as exception:
        reply_text = ERROR_TEXT_PATTERN.format(
            description=_("User couldn't be charged. Review input.")
        )
        logger.exception(
            _("Something went wrong while charging user: {exception}.").format(
                exception=exception
            )
        )

    else:
        reply_text = CHARGE_TEXT_PATTERN.format(transfer=transfer)
        logger.info(
            _("{recipient_username} charged {sender_username} {amount} justines").format(
                amount=amount,
                sender_username=sender_username,
                recipient_username=recipient_username,
            )
        )

    await update.message.reply_text(reply_text)

if __name__ == "__main__":
    api_token = config.api_token or typer.prompt(_("API token"), hide_input=True)
    app = Application.builder().token(api_token).build()

    for statement in menu:
        app.add_handler(statement.handler)

    logger.info(_("Polling..."))
    app.run_polling(poll_interval=config.poll_interval)
