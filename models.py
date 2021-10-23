from datetime import datetime as dt

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


class MovieTree(BaseModel):
    id_from = ForeignKeyField(Members, field='id_telegram', related_name='recommended',
                              on_delete='cascade')
    id_to = ForeignKeyField(Members, field='id_telegram', related_name='watcher')
    date = DateTimeField(default=dt.now())
    movie = CharField()


if __name__ == '__main__':
    Members.create_table()
    MovieTree.create_table()
