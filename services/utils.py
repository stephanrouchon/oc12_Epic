import re
import datetime
import click


def is_valid_email(email):
    # Expression régulière simple pour valider un email
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None


def date_is_valid(date):
    try:
        date = datetime.strptime(date, "%Y-%m-%d")
        return date
    except ValueError:
        click.echo("Format de date invalide. utilisez YYYY-MM-DD")
        return None
