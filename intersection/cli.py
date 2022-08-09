import click

from .game import updater


@click.command()
def start():
    updater.start_polling(drop_pending_updates=True)
