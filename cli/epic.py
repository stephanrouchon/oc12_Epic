import click
from cli.commands.user_commands import user
from cli.commands.auth_commands import auth
from cli.commands.client_commands import client
from cli.commands.contract_commands import contract
from cli.commands.event_commands import event


@click.group()
def epic():
    pass


epic.add_command(auth)
epic.add_command(user)
epic.add_command(client)
epic.add_command(contract)
epic.add_command(event)

if __name__ == "__main__":
    epic()
