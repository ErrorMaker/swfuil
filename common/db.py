__author__ = 'Scott Stamp <scott@hypermine.com>'
from peewee import *
import os

database_name = os.getenv('SWFUTIL_DB_ENV_MYSQL_DATABASE', 'swfs')
database_host = os.getenv('SWFUTIL_DB_PORT_3306_TCP_ADDR', 'localhost')
database_username = os.getenv('SWFUTIL_DB_USER', 'root')
database_password = os.getenv('SWFUTIL_DB_ENV_MYSQL_ROOT_PASSWORD', 'root')
database = MySQLDatabase(database_name, host=database_host, user=database_username, passwd=database_password)


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
    def create_tables():
        database.connect()
        print(database.get_tables())
        database.create_tables([SWF, Hotel], True)

    @staticmethod
    def insert_value(habbo):
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