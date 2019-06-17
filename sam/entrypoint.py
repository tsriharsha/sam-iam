import click

from .config.cmds import configure
from .iam.cmds import iam


@click.group()
def cli():
    """
        Basic Setup of the Ping 2 Aws Federated Programmatic Access Creation via a manual or automated process.
    """
    pass


cli.add_command(configure)
cli.add_command(iam)