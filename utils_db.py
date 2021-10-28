from peewee import DoesNotExist, Select

from models import Members, Purposes, Rolls, Movies, State


def get_member(id_telegram: int) -> Members:
    """Возвращает найденного пользователя по ИД"""
   
    result = Members.select().where(Members.id_telegram == id_telegram).get()
    return result


def check_have_member(id_member: int) -> bool:
    """
    Проверяет существует ли в базе переданный ID
    """
    select = Members.select()
    result = select.where(Members.id_telegram == id_member).exists()

    return result


def get_first_name(id_member: int) -> str:
    """
    Возвращает имя учатника.
    """
    member = get_member(id_telegram=id_member)
    return member.first_name


def get_last_name(id_member: int) -> str:
    """
    Возврашает фамилию участника.
    """
    member = get_member(id_telegram=id_member)
    return member.last_name



def check_active(id_telegram: int) -> bool:
    """Проверяет активен ли пользователь по ID"""
    member = get_member(id_telegram=id_telegram)
    result = member.is_active

    return result


def create_user(id_member: int, first_name: str, last_name: str):
    """Создает в БД строку пользователя"""
    Members.create(id_telegram=id_member,
                   first_name=first_name,
                   last_name=last_name)


def activated_user(id_member: int):
    """Активирует пользователя"""
    member = get_member(id_telegram=id_member)
    member.is_active = True
    member.save()


def deactivated_user(id_member: int):
    """Активирует пользователя"""
    member = get_member(id_telegram=id_member)
    member.is_active = False
    member.save()


def count_active_members() -> int:
    """Возвращает кол-во активных участников"""
    result = Members.select().where(Members.is_active == True).count()
    return result


def get_ids_active_members() -> list:
    """Возвращает ид активных пользователей"""
    select = Members.select().where(Members.is_active==True)
    result = []
    for member in select:
        result.append(member.id_telegram)
    return result

def make_purpose_rec(id_advisor: int, id_watcher: int, id_roll:int):
    Purposes.create(id_from=id_advisor, id_to=id_watcher, id_roll=id_roll)


def get_id_watcher_from_advisor_last_roll(id_advisor: int) -> int:
    roll = Rolls.select().where(Rolls.status==0).order_by(Rolls.id.desc()).get()
    result = roll.purposes.select().where(Purposes.id_from==id_advisor).get()
    id_watcher = result.id_to.id_telegram

    return id_watcher


def get_id_advisor_from_wathcer_last_roll(id_watcher: int) -> int:
    roll = Rolls.select().where(Rolls.status==0).order_by(Rolls.id.desc()).get()
    result = roll.purposes.select().where(Purposes.id_to==id_watcher).get()
    id_advisor = result.id_from.id_telegram

    return id_advisor


def get_ids_advisor_active_roll():
    """
    Возвращает id всех участников которые задают фильм в последнем ролле.
    """
    result = []
    roll = Rolls.select().where(Rolls.status==0).order_by(Rolls.id.desc()).get()
    select = roll.purposes.select().where(Purposes.movie==None)
    for purpose in select:
        result.append(purpose.id_from.id_telegram)
    
    return result


def get_ids_watchers_active_roll():
    """
    Возвращает id всех участников которые задают фильм в последнем ролле.
    """
    result = []
    roll = Rolls.select().where(Rolls.status==0).order_by(Rolls.id.desc()).get()
    select = roll.purposes.select().where(Purposes.movie==None)
    for purpose in select:
        result.append(purpose.id_to.id_telegram)
    
    return result


def get_movie_or_create(movie: str):
    """
    Находит фильм в бд или создает его, возвращает id фильма.
    """
    try:
        result = Movies.select().where(Movies.name==movie).get()
    except DoesNotExist:
        result = Movies.create(name=movie)
    
    return result.id


def set_movie_for_purpose(id_watcher: int, title_movie: str):
    id_movie = get_movie_or_create(movie=title_movie)
    roll = Rolls.select().where(Rolls.status==0).order_by(Rolls.id.desc()).get()
    purpose = roll.purposes.select().where(
        Purposes.id_to==Members.select().where(Members.id_telegram==id_watcher)
        ).get()
    purpose.movie = id_movie
    purpose.save()


def get_or_create_state_user(id_member: int):
    """
    Получает или создает статус для пользователя.
    """
    member = get_member(id_telegram=id_member)
    try:
        state = State.select().where(State.user==member.id_telegram).get()
    except DoesNotExist:
        state = State.create(user=member.id_telegram)
    return state



def set_state(id_member: int, status: str):
    """
    Назначение статуса пользователю.
    """
    state = get_or_create_state_user(id_member=id_member)
    state.status = status
    state.save()


def get_state(id_member: int):
    """
    Получение статуса пользователя.
    """
    state = get_or_create_state_user(id_member=id_member)
    return state.status



def reset_state(id_member: int):
    """
    Сброс статуса пользователя.
    """
    state = get_or_create_state_user(id_member=id_member)
    state.status = None
    state.save()


def create_roll():
    roll = Rolls.create()

    return roll.id
