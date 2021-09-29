from peewee import *


db = SqliteDatabase('movie_choice.db')


class Members(Model):
    id_telegram = IntegerField(unique=True, column_name='Ид телеграма', primary_key=True)
    nickname = CharField()
    is_active = BooleanField(default=True)

    def __repr__(self):
        return f'{self.nickname} - {self.id_telegram}'

    class Meta:
        database = db


class MovieTree(Model):
    id_from = ForeignKeyField(Members, field='id_telegram', related_name='recommended')
    id_to = ForeignKeyField(Members, field='id_telegram', related_name='watcher')
    date = DateField()
    movie = CharField()

    class Meta:
        database = db

