__author__ = 'Scott Stamp <scott@hypermine.com>'
from peewee import *

database = MySQLDatabase('swfs', host='localhost', user='root', passwd='root')


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