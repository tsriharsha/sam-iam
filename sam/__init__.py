from functools import wraps

import click
from pyfiglet import Figlet


def load_logo(f):
    @wraps(f)
    def wrapped(*args, **kwargs):
        fig = Figlet(font='slant')
        click.echo(click.style(fig.renderText("SAMIAM"), fg='green'))
        r = f(*args, **kwargs)
        return r

    return wrapped