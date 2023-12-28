from peewee import *


class OUI(Model):
    prefix = CharField()
    org = CharField()


class LastUpdate(Model):
    timestamp = TextField()