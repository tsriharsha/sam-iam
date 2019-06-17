import click

from .. import load_logo
from ..config import SAMIAMConfig, SECTION, key_list


@click.command("configure")
@load_logo
def configure():
    """
        Configuring the default settings of samiam
    """

    from ..utils.chain import attempt_correct_drivers

    click.secho('Attempting to load correct pre-installed drivers.', fg='green')
    chrome_driver_path = attempt_correct_drivers()

    if chrome_driver_path is None:
        chrome_driver_path = click.prompt("Enter your chrome driver location (absolute path)", type=str)
    else:
        click.secho('Found correct drivers automatically in path: ' + chrome_driver_path
                    , fg='green')

    sso_url = click.prompt("Enter your sso url", type=str)

    with SAMIAMConfig(SECTION) as sic:
        sic.set(SECTION, key_list[0], str(chrome_driver_path))
        sic.set(SECTION, key_list[1], str(sso_url))
