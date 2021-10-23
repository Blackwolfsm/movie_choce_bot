from peewee import DoesNotExist

from models import Members


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