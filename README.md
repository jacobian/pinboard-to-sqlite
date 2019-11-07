# Save data from Pinboard to a SQLite database.

Inspired by (and using libraries from) [Simon Willison's Dogsheep
project](https://github.com/dogsheep). You're probably going to want to run
[Datasette](https://github.com/simonw/datasette) on the resulting db.

## How to install

```
$ pip install pinboard-to-sqlite
```

## Authentication

Run:

```
$ pinboard-to-sqlite auth
```

This will direct you to https://pinboard.in/settings/password to find your API
token, which you'll then paste into the terminal. This'll get saved in an
`auth.json` file, which subsequent commands will pick up.

To save to a different file, see the `-a` / `--auth` flag.

## Fetching posts

Run:

```
$ pinboard-to-sqlite posts pinboard.db
```

Where `pinboard.db` is the name of the database you'd like to save posts to.
Note that the API this uses has a rate limit of once per minute, so don't run
this command more than once per minute (I don't know why you would). This
doesn't seem to be enforced fairly loosely, but be careful anyway.
