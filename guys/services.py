from .models import Guy

def load_guys(count: int) -> int:
    """Cоздаем записи в базе данных для полученных тестовых людей"""
    if count <= 0:
        return 0

    guys = [
        Guy(
            gender='woman' if i % 2 == 0 else 'man',
            first_name=f'TestFirst{i}',
            last_name=f'TestLast{i}',
            phone=f'+7 (900) 000-00-{i % 100:02d}',
            email=f'test{i}@example.com',
            address=f'Город {i}, ул. Тестовая, д. {i}',
        )
        for i in range(count)
    ]
    created = Guy.objects.bulk_create(guys)
    return len(created)
