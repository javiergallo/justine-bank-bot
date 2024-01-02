USERNAME_REGEX = r"^(?=(?:[0-9_]*[A-Za-z]){3})[A-Za-z0-9_]{5,}$"

ERROR_TEXT_PATTERN = "Uy! Algo salió mal! {description} \U0001F974"
START_TEXT_PATTERN = (
    "¡Hola @{username}! Soy el bot administrador del Banco de Justines. Enviá "
    "/help si querés que te cuente qué se puede hacer en el Banco de Justines."
)
WALLET_TEXT_PATTERN = "@{wallet.owner_username}: {wallet.balance} justines."
ISSUE_TEXT_PATTERN = (
    "{issue.creation_datetime:%d-%m-%Y %H:%M:%S}: "
    "{issue.amount} justines emitidos "
    "a @{issue.recipient.owner_username}"
)
TRANSFER_TEXT_PATTERN = (
    "{transfer.creation_datetime:%d-%m-%Y %H:%M:%S}: "
    "{transfer.amount} justines transferidos "
    "de @{transfer.sender.owner_username} "
    "a @{transfer.recipient.owner_username}"
)