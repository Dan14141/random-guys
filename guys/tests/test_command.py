import pytest
import responses
from django.conf import settings
from django.core.management import call_command

from guys.models import Guy


@pytest.mark.django_db
class TestLoadInitialGuysCommand:
    @responses.activate
    def test_command_loads_when_db_empty(self, sample_api_records):
        responses.add(
            responses.GET,
            settings.RANDOMDATATOOLS_URL,
            json=sample_api_records,
            status=200,
        )
        call_command('load_initial_guys', '--count=3')
        assert Guy.objects.count() == 3

    @responses.activate
    def test_command_skips_when_db_non_empty(self, guy, sample_api_records):
        responses.add(
            responses.GET,
            settings.RANDOMDATATOOLS_URL,
            json=sample_api_records,
            status=200,
        )
        call_command('load_initial_guys', '--count=3')
        # Пропуск происходит перед HTTP-запросом, остается только один существующий пользователь
        assert Guy.objects.count() == 1
        assert len(responses.calls) == 0

    @responses.activate
    def test_command_force_loads_when_db_non_empty(self, guy, sample_api_records):
        responses.add(
            responses.GET,
            settings.RANDOMDATATOOLS_URL,
            json=sample_api_records,
            status=200,
        )
        call_command('load_initial_guys', '--count=3', '--force')
        # 1 был + 3 новых = 4 стало
        assert Guy.objects.count() == 4

    @responses.activate
    def test_command_handles_api_failure(self):
        responses.add(
            responses.GET,
            settings.RANDOMDATATOOLS_URL,
            status=500,
        )
        call_command('load_initial_guys', '--count=5')
        assert Guy.objects.count() == 0
