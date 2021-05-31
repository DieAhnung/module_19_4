from api import PetFriends
from settings import valid_email, valid_password, invalid_password
import pytest

pf = PetFriends()


# Аутентификация/авторизация
def test_get_api_key_for_valid_user(email=valid_email, password=valid_password):
    """проверка авторизации с валидным парорлем"""
    status, result = pf.get_api_key(email, password)
    assert status == 200
    assert 'key' in result


def test_get_api_key_for_invalid_user(email=valid_email, password=invalid_password):
    """Проверка авторизации с невалидным паролем"""
    status, result = pf.get_api_key(email, password)
    assert status == 403
    assert 'key' not in result
    assert "This user wasn't found in database" in result


def test_get_all_pets_with_invalid_key(filter=''):
    """ Internal Server Error 500 при неправильном auth_key """

    _, auth_key = pf.get_api_key(valid_email, valid_password)
    status, result = pf.get_list_of_pets(auth_key, filter + 'ddt')

    assert status == 500  # «внутренняя ошибка сервера»


# Список питомцев
def test_get_all_pets_with_valid_key(filter=''):
    """Выдача питомцев без фильтров"""
    _, auth_key = pf.get_api_key(valid_email, valid_password)
    status, result = pf.get_list_of_pets(auth_key, filter)
    assert status == 200
    assert len(result['pets']) > 0


def test_get_my_pets_with_valid_key(filter='my_pets'):
    """Выдача списка моих питомцев"""
    _, auth_key = pf.get_api_key(valid_email, valid_password)
    status, result = pf.get_list_of_pets(auth_key, filter)
    assert status == 200
    assert len(result['pets']) == 0 or len(result['pets']) > 0


def test_get_pets_with_wrong_filter(filter='123'):
    """Выдача питомцев с несуществующим фильтром"""
    _, auth_key = pf.get_api_key(valid_email, valid_password)
    status, result = pf.get_list_of_pets(auth_key, filter)
    assert status != 200
    assert "Filter value is incorrect" in result


# Создание / обновление питомцев
def test_create_pet_simple(name='Котенька', animal_type='cat', age='9'):
    """Создание питомца без фото"""
    _, auth_key = pf.get_api_key(valid_email, valid_password)
    status, result = pf.create_pet_simple(auth_key, name, animal_type, age)
    assert status == 200
    assert result['name'] == name
    assert result['animal_type'] == animal_type
    assert result['age'] == age
    assert result['id'] is not None


def test_create_pet_with_photo(name='Котенька', animal_type="КОТ", age='9', photo='images/Screenshot_1.jpg'):
    """Создание питомца с фото"""
    _, auth_key = pf.get_api_key(valid_email, valid_password)
    status, result = pf.create_pet_with_photo(auth_key, name, animal_type, age, photo)

    assert status == 200
    assert result['name'] == name
    assert result['animal_type'] == animal_type
    assert result['age'] == age
    assert result['id'] is not None
    assert result['pet_photo'] is not None
    assert 'jpeg' in result['pet_photo']


def test_update_pet(name='Котик', animal_type='кот', age='99'):
    """Обновление информции о питомце"""
    _, auth_key = pf.get_api_key(valid_email, valid_password)
    _, result = pf.get_list_of_pets(auth_key, filter='my_pets')
    pet_id = result['pets'][0]['id']
    status, result = pf.update_pet_info(auth_key, pet_id, name, animal_type, age)

    assert status == 200
    assert result['name'] == name
    assert result['animal_type'] == animal_type
    assert result['age'] == age


def test_add_pet_photo(photo='images/Screenshot_2.jpg'):
    """Добавление фотографии существующему питомцу"""
    _, auth_key = pf.get_api_key(valid_email, valid_password)
    _, result = pf.get_list_of_pets(auth_key, filter='my_pets')
    pet_id = result['pets'][0]['id']
    status, result = pf.add_photo_of_pet(auth_key, pet_id, photo)

    assert status == 200
    assert result['pet_photo'] is not None
    assert 'jpeg' in result['pet_photo']


# Удаление питомцев
def test_delete_pet():
    """Удаление существующего питомца"""
    _, auth_key = pf.get_api_key(valid_email, valid_password)
    _, result = pf.get_list_of_pets(auth_key, filter='my_pets')
    pet_id = result['pets'][0]['id']
    status, result = pf.delete_pet(auth_key, pet_id)

    assert status == 200


def test_failed_delete_pet_with_wrong_id():
    """ Удаление питомца с несуществующим id"""
    _, auth_key = pf.get_api_key(valid_email, valid_password)
    _, my_pets = pf.get_list_of_pets(auth_key, "my_pets")
    if len(my_pets['pets']) == 0:
        pf.create_pet_with_photo(auth_key, "Котенька", "кот", "3", "images/Screenshot_1.jpg")
        _, my_pets = pf.get_list_of_pets(auth_key, "my_pets")
    pet_id = 10000000000
    with pytest.raises(Exception):
        print('Deleting with wrong id throws Exception')
        status, _ = pf.delete_pet(auth_key, pet_id)
