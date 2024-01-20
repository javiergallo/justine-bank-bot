from justine_bank.localization import _

USERNAME_REGEX = r"^(?=(?:[0-9_]*[a-z]){3})[a-z0-9_]{5,}$"

NO_ITEMS_TEXT_PATTERN = _("There are no {items_type}")
ERROR_TEXT_PATTERN = _("Something went wrong. {description}")
START_TEXT_PATTERN = _("Hello @{username}")
WALLET_TEXT_PATTERN = _("@{wallet.owner_username}: {wallet.balance} justines.")
ISSUE_TEXT_PATTERN = _(
    "{issue.creation_datetime:%d-%m-%Y %H:%M:%S}: "
    "{issue.amount} justines issued "
    "for @{issue.recipient.owner_username}"
)
TRANSFER_TEXT_PATTERN = _(
    "{transfer.creation_datetime:%d-%m-%Y %H:%M:%S}: "
    "{transfer.amount} justines transferred "
    "from @{transfer.sender.owner_username} "
    "to @{transfer.recipient.owner_username}"
)
CHARGE_TEXT_PATTERN = _(
    "{transfer.creation_datetime:%d-%m-%Y %H:%M:%S}: "
    "@{transfer.recipient.owner_username} charged "
    "@{transfer.sender.owner_username} "
    "{transfer.amount} justines"
)
