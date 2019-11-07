import click
import os
import json
import sqlite_utils
import requests
import dateutil.parser


@click.group()
@click.version_option()
def cli():
    "Save data from Pinboard to a SQLite database"


@cli.command()
@click.option(
    "-a",
    "--auth",
    type=click.Path(file_okay=True, dir_okay=False, allow_dash=False),
    default="auth.json",
    help="Path to save token to",
    show_default=True,
)
def auth(auth):
    "Save authentication credentials to a JSON file"
    click.echo("Find your API token here: https://pinboard.in/settings/password")
    click.echo(
        "Paste the whole thing including your username "
        "(e.g. yourname:xxxyyyzzz) below."
    )
    click.echo()
    pinboard_token = click.prompt("API Token")
    auth_data = json.load(open(auth)) if os.path.exists(auth) else {}
    auth_data["pinboard_token"] = pinboard_token
    json.dump(auth_data, open(auth, "w"))


@cli.command()
@click.argument(
    "database",
    required=True,
    type=click.Path(file_okay=True, dir_okay=False, allow_dash=False),
)
@click.option(
    "-a",
    "--auth",
    type=click.Path(file_okay=True, dir_okay=False, allow_dash=False, exists=True),
    default="auth.json",
    help="Path to read auth token from",
    show_default=True,
)
@click.option(
    "--since",
    is_flag=True,
    default=False,
    help="Pull new posts since last saved post in DB",
)
@click.option("--since-date", metavar="DATE", help="Pull new posts since DATE")
def posts(database, auth, since, since_date):
    if since and since_date:
        raise click.UsageError("use either --since or --since-date, not both")

    token = json.load(open(auth))["pinboard_token"]
    params = {"format": "json", "auth_token": token}

    db = sqlite_utils.Database(database)

    if since and db["posts"].exists:
        since_date = db.conn.execute("SELECT max(time) FROM posts;").fetchone()[0]
    if since_date:
        params["fromdt"] = (
            dateutil.parser.parse(since_date)
            .replace(microsecond=0, tzinfo=None)
            .isoformat()
            + "Z"
        )

    posts = requests.get(f"https://api.pinboard.in/v1/posts/all", params=params).json()
    _save_posts(db, posts)


def _save_posts(db, posts):
    # Convert/coerce some fields
    for post in posts:
        post["shared"] = post["shared"] == "yes"
        post["toread"] = post["toread"] == "yes"
        post["time"] = dateutil.parser.parse(post["time"])
        post["tags"] = json.dumps(post["tags"].split())

    db["posts"].upsert_all(
        posts,
        pk="hash",
        column_order=[
            "hash",
            "href",
            "description",
            "extended",
            "meta",
            "time",
            "shared",
            "toread",
            "tags",
        ],
    )


# TODO: notes?
