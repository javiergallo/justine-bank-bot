import gettext

translate = gettext.translation('justine-bank-bot', './locales', fallback=True)
_ = translate.gettext
