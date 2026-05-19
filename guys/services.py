"""Бизнес логика для взаимодействия с внешним API"""
from __future__ import annotations

import logging

import requests
from django.conf import settings
from django.db import transaction

from .models import Guy

logger = logging.getLogger(__name__)


class RandomGuysAPIError(Exception):
    """Исключение при ошибочном запросе к внешнему API"""

def fetch_guys_from_api(count: int) -> list[dict]:
    """Получаем нужное кол-во людей из внешнего API"""
    if count <= 0:
        return []

    url = settings.RANDOMDATATOOLS_URL
    try:
        response = requests.get(url, params={'count': count}, timeout=30)
        response.raise_for_status()
        data = response.json()
    except requests.RequestException as exc:
        raise RandomGuysAPIError(f'Network error: {exc}') from exc
    except ValueError as exc:
        raise RandomGuysAPIError(f'Invalid JSON in response: {exc}') from exc

    # API возвращает словарь при count=1, иначе список
    if isinstance(data, dict):
        data = [data]
    if not isinstance(data, list):
        raise RandomGuysAPIError(f'Unexpected response shape: {type(data)}')
    return data

def guy_from_api_dict(data: dict) -> Guy:
    """Преобразуем запись в объект Guy"""
    return Guy(
        gender=data.get('GenderCode', ''),
        first_name=data.get('FirstName', ''),
        last_name=data.get('LastName', ''),
        phone=data.get('Phone', ''),
        email=data.get('Email', ''),
        address=data.get('Address', ''),
    )

@transaction.atomic
def load_guys(count: int) -> int:
    """Массово создаем записи в базе данных для полученных людей"""
    raw_records = fetch_guys_from_api(count)
    guys = [guy_from_api_dict(item) for item in raw_records]
    created = Guy.objects.bulk_create(guys, batch_size=500)
    logger.info('Loaded %d guys from API', len(created))
    return len(created)