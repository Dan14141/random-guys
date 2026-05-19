import pytest
import responses
from django.conf import settings

from guys.models import Guy
from guys.services import (
    RandomGuysAPIError,
    fetch_guys_from_api,
    load_guys,
)


@pytest.mark.django_db
class TestFetchGuysFromAPI:
    @responses.activate
    def test_fetch_returns_list(self, sample_api_records):
        responses.add(
            responses.GET,
            settings.RANDOMDATATOOLS_URL,
            json=sample_api_records,
            status=200,
        )
        result = fetch_guys_from_api(3)
        assert len(result) == 3
        assert result[0]['FirstName'] == 'TestFirst0'

    @responses.activate
    def test_fetch_normalizes_single_dict_to_list(self, sample_api_record):
        """API возвращает словарь, когда count=1, его нужно нормализовать"""
        responses.add(
            responses.GET,
            settings.RANDOMDATATOOLS_URL,
            json=sample_api_record,
            status=200,
        )
        result = fetch_guys_from_api(1)
        assert isinstance(result, list)
        assert len(result) == 1
        assert result[0]['FirstName'] == 'Василиса'

    def test_fetch_zero_count_returns_empty(self):
        # При count=0 HTTP-запрос не нужно выполнять
        assert fetch_guys_from_api(0) == []

    @responses.activate
    def test_fetch_raises_on_http_error(self):
        responses.add(
            responses.GET,
            settings.RANDOMDATATOOLS_URL,
            status=500,
        )
        with pytest.raises(RandomGuysAPIError):
            fetch_guys_from_api(10)

    @responses.activate
    def test_fetch_raises_on_invalid_json(self):
        responses.add(
            responses.GET,
            settings.RANDOMDATATOOLS_URL,
            body='not valid json',
            status=200,
            content_type='application/json',
        )
        with pytest.raises(RandomGuysAPIError):
            fetch_guys_from_api(10)

    @responses.activate
    def test_fetch_raises_on_unexpected_shape(self):
        responses.add(
            responses.GET,
            settings.RANDOMDATATOOLS_URL,
            json='just a string',
            status=200,
        )
        with pytest.raises(RandomGuysAPIError):
            fetch_guys_from_api(10)

    @responses.activate
    def test_fetch_sends_count_param(self, sample_api_records):
        responses.add(
            responses.GET,
            settings.RANDOMDATATOOLS_URL,
            json=sample_api_records,
            status=200,
        )
        fetch_guys_from_api(3)
        assert len(responses.calls) == 1
        assert 'count=3' in responses.calls[0].request.url


@pytest.mark.django_db
class TestLoadPeople:
    @responses.activate
    def test_load_creates_records(self, sample_api_records):
        responses.add(
            responses.GET,
            settings.RANDOMDATATOOLS_URL,
            json=sample_api_records,
            status=200,
        )
        created = load_guys(3)
        assert created == 3
        assert Guy.objects.count() == 3
        assert Guy.objects.filter(first_name='TestFirst0').exists()

    @responses.activate
    def test_load_propagates_api_error(self):
        responses.add(
            responses.GET,
            settings.RANDOMDATATOOLS_URL,
            status=503,
        )
        with pytest.raises(RandomGuysAPIError):
            load_guys(10)
        assert Guy.objects.count() == 0
