import logging

from dataclasses import dataclass
from typing import List, Optional, Tuple

from telegram import Update
from telegram.ext import CommandHandler, ContextTypes

from justine_bank.localization import _
from justine_bank.settings import config
from justine_bank.utils import clean_username

logger = logging.getLogger('abc')


@dataclass
class CommandStatement:
    handler: CommandHandler
    arg_names: Optional[Tuple[str, ...]] = None
    restricted: bool = False
    help_text: str = ""
    example: str = ""


class Menu:
    _statements: List[CommandStatement]

    def __init__(self):
        self._statements = []

    def add_statement(self, statement: CommandStatement):
        self._statements.append(statement)
    
    def command(
        self,
        name: str,
        arg_names: Optional[Tuple[str, ...]] = None,
        restricted: bool = False,
        **kwargs
    ):
        arg_names = arg_names or []

        def add_statement(callback):
            async def run_command(
                update: Update,
                context: ContextTypes.DEFAULT_TYPE,
            ):
                username = clean_username(update.message.from_user.username)

                if restricted and username not in config.staff_usernames:
                    reply_text = _(
                        "This command is restricted to staff users only"
                    )
                    await update.message.reply_text(
                        reply_text,
                        parse_mode='Markdown'
                    )
                    logger.error(_("Command restricted to staff"))
                else:
                    await callback(update=update, context=context)

            handler = CommandHandler(name, run_command)
            statement = CommandStatement(
                handler=handler,
                arg_names=arg_names,
                restricted=restricted,
                **kwargs
            )
            self.add_statement(statement)
            return run_command
        return add_statement

    def __iter__(self):
        return iter(self._statements)
