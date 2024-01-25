from dataclasses import dataclass
from typing import List, Optional, Tuple

from telegram.ext import CommandHandler


@dataclass
class CommandStatement:
    handler: CommandHandler
    arg_names: Optional[Tuple[str, ...]] = None
    help_text: str = ""
    example: str = ""
    restricted: bool = False


class Menu:
    _statements: List[CommandStatement]

    def __init__(self):
        self._statements = []

    def add_statement(self, statement: CommandStatement):
        self._statements.append(statement)
    
    def command(self, name: str, arg_names: Optional[Tuple[str, ...]] = None, **kwargs):
        arg_names = arg_names or []

        def add_statement(callback):
            handler = CommandHandler(name, callback)
            self.add_statement(CommandStatement(handler, arg_names, **kwargs))
            return callback
        return add_statement

    def __iter__(self):
        return iter(self._statements)
