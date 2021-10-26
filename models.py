from datetime import datetime as dt
from typing import NoReturn

from peewee import *


NAME_DB = 'movie_choice.db'
db = SqliteDatabase(NAME_DB)


class BaseModel(Model):
    class Meta:
        database = db


class Members(BaseModel):
    id_telegram = IntegerField(unique=True, verbose_name='Ид телеграма', primary_key=True)
    first_name = CharField(max_length=100)
    last_name = CharField(max_length=100)
    date_registration = DateTimeField(default=dt.now())
    is_active = BooleanField(default=True)

    def __str__(self):
        return f'{self.first_name} {self.last_name} (id: {self.id_telegram})'
    
    class Meta:
        order_by = ('date_registration',)


class Movies(BaseModel):
    name = CharField(max_length=100)
    year = IntegerField(null=True, default=None)
    avg_score = FloatField(null=True, default=None)

    def __str__(self):
        return f'{self.name}'


class Rolls(BaseModel):
    date = DateTimeField(default=dt.now())
    status = IntegerField(choices=((0, 'Идет назначение фильмов'),
                                   (1, 'Все фильмы назначены'),
                                   (2, 'Все фильмы просмотрены'),
                                   (3, 'Все фильмы оценены')),
                          default=0)


class Purposes(BaseModel):
    id_roll = ForeignKeyField(Rolls, field='id', related_name='purposes')
    id_from = ForeignKeyField(Members, field='id_telegram', related_name='recommended',
                              on_delete='cascade')
    id_to = ForeignKeyField(Members, field='id_telegram', related_name='watcher')
    date = DateTimeField(default=dt.now())
    movie = ForeignKeyField(Movies, field='id', 
                            related_name='watch_history', null=True, default=None)
    viewed = BooleanField(default=False)
    score = IntegerField(null=True, default=None)


if __name__ == '__main__':
    Members.create_table()
    Purposes.create_table()
    Movies.create_table()
    Rolls.create_table()
