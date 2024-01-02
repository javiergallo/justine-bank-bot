USERNAME_REGEX = r"^(?=(?:[0-9_]*[A-Za-z]){3})[A-Za-z0-9_]{5,}$"

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