import pytest

from guys.models import Guy


SAMPLE_API_RECORD = {
    'LastName': 'Некрестьянова',
    'FirstName': 'Василиса',
    'FatherName': 'Георгьевна',
    'Phone': '+7 (937) 301-49-94',
    'Email': 'vasilisa1961@yandex.ru',
    'Gender': 'Женщина',
    'GenderCode': 'woman',
    'Address': 'Россия, г. Рыбинск, Белорусская ул., д. 1 кв.106',
}


@pytest.fixture
def sample_api_record():
    return SAMPLE_API_RECORD.copy()


@pytest.fixture
def sample_api_records():
    """Возвращает список из 3 различных записей API"""
    records = []
    for i in range(3):
        rec = SAMPLE_API_RECORD.copy()
        rec['FirstName'] = f'TestFirst{i}'
        rec['LastName'] = f'TestLast{i}'
        rec['Email'] = f'test{i}@example.com'
        records.append(rec)
    return records


@pytest.fixture
def guy(db):
    return Guy.objects.create(
        gender='woman',
        first_name='Василиса',
        last_name='Некрестьянова',
        phone='+7 (937) 301-49-94',
        email='vasilisa1961@yandex.ru',
        address='Россия, г. Рыбинск, Белорусская ул., д. 1 кв.106',
    )


@pytest.fixture
def many_people(db):
    """Создаём 10 человек для постраничной навигации и случайных тестов"""
    people = [
        Guy(
            gender='man' if i % 2 else 'woman',
            first_name=f'First{i}',
            last_name=f'Last{i}',
            phone=f'+7 (900) 000-00-{i:02d}',
            email=f'user{i}@example.com',
            address=f'City {i}',
        )
        for i in range(10)
    ]
    return Guy.objects.bulk_create(people)
