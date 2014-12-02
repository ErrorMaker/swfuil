__author__ = 'Scott Stamp <scott@hypermine.com>'
from peewee import *
import os
from urllib.parse import urlparse


if 'MYSQL_URL' in os.environ:
    # Looks like we're in Stackato
    url = urlparse(os.environ['MYSQL_URL'])
    name = url.path[1:]
    host = url.hostname
    username = url.username
    password = url.password
    port = url.port
else:
    # Defaults, we're probably not running on Stackato
    name = os.getenv('DB_NAME', 'swfs')
    host = os.getenv('DBL_HOST', 'localhost')
    username = os.getenv('DB_USER', 'root')
    password = os.getenv('DB_PASSWORD', 'root')
    port = 3306

database = MySQLDatabase(name, host=host,
                         user=username, passwd=password, port=port)


class SWF(Model):
    name = CharField(primary_key=True)
    origPublicModulus = CharField()
    origPublicExponent = CharField()
    newPublicModulus = CharField()
    newPublicExponent = CharField()
    newPrivateExponent = CharField()

    class Meta:
        database = database


class Hotel(Model):
    url = CharField()
    build = CharField(primary_key=True)
    latest = ForeignKeyField(SWF, related_name='hotels')

    class Meta:
        database = database


class DatabaseHelper:
    @staticmethod
    def setup_db():
        """Setup the tables in the database, unless they exist."""
        database.create_tables([SWF, Hotel], True)

    @staticmethod
    def insert_value(habbo):
        """Insert the results from an instance of backend.habbo.Habbo."""
        with database.transaction():
            try:
                swf = SWF.create(
                    name=habbo.swfName,
                    origPublicModulus=habbo.origKey['n'],
                    origPublicExponent=habbo.origKey['e'],
                    newPublicModulus=habbo.newKey['n'],
                    newPublicExponent=habbo.newKey['e'],
                    newPrivateExponent=habbo.newKey['d']
                )
            except:
                swf = SWF.select().where(SWF.name == habbo.swfName)

            try:
                Hotel.create(
                    url=habbo.hotel,
                    build=habbo.buildVersion,
                    latest=swf
                )
            except:
                # We might already have this version stored in the database bcause I'm fucking tired.
                pass