import click
import logging
import sys

# from .package_specification import from_prompt, install_package, publish_package
log = logging.getLogger(__name__)
console_handler = logging.StreamHandler(sys.stderr)

# logging.basicConfig(level=logging.INFO)


@click.group()
@click.option('--debug', default=False)
def main(debug):
    if debug:
        logging.basicConfig(level=logging.DEBUG)


@main.command()
def init():
    pass


@main.command()
@click.argument('path')
def install(path):
    pass


@main.command()
def publish():
    pass


if __name__ == '__main__':
    main()
