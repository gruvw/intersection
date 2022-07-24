import click

from .telegram_bot import updater


@click.command()
def start():
    updater.start_polling()
    # updater.idle()
