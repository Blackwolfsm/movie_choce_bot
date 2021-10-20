from datetime import datetime as dt

from peewee import *


db = SqliteDatabase('movie_choice.db')


class BaseModel(Model):
    class Meta:
        database = db


class Members(BaseModel):
    id_telegram = IntegerField(unique=True, verbose_name='Ид телеграма', primary_key=True)
    nickname = CharField()
    is_active = BooleanField(default=True)

    def __repr__(self):
        return f'{self.nickname} - {self.id_telegram}'


class MovieTree(BaseModel):
    id_from = ForeignKeyField(Members, field='id_telegram', related_name='recommended',
                              on_delete='cascade')
    id_to = ForeignKeyField(Members, field='id_telegram', related_name='watcher')
    date = DateTimeField(default=dt.now())
    movie = CharField()


if __name__ == '__main__':
    Members.create_table()
    MovieTree.create_table()
