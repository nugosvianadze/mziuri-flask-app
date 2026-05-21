import click
from flask import Flask
from flask_sqlalchemy import SQLAlchemy


def register_commands(app: Flask, db: SQLAlchemy):
    @app.cli.command("init-db")
    def init_db_command():
        db.create_all()
        click.echo("Database initialized.")

    @app.cli.command("drop-all-tables")
    def drop_all_tables():
        db.drop_all()
        click.echo("Database cleared!")
