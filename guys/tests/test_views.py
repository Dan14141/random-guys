import pytest
import responses
from django.conf import settings
from django.urls import reverse


@pytest.mark.django_db
class TestIndexView:
    def test_index_renders_empty(self, client):
        response = client.get(reverse('guys:index'))
        assert response.status_code == 200
        assert b'people' in response.content.lower() or response.context['total_count'] == 0

    def test_index_shows_people(self, client, many_people):
        response = client.get(reverse('guys:index'))
        assert response.status_code == 200
        assert response.context['total_count'] == 10
        # На первой странице представлены все 10 (размер страницы по умолчанию 50)
        assert len(response.context['page_obj'].object_list) == 10

    def test_index_pagination(self, client, many_people, settings):
        settings.PEOPLE_PER_PAGE = 3
        response = client.get(reverse('guys:index'))
        assert response.status_code == 200
        assert len(response.context['page_obj'].object_list) == 3
        # Page 2
        response = client.get(reverse('guys:index') + '?page=2')
        assert response.status_code == 200
        assert len(response.context['page_obj'].object_list) == 3


@pytest.mark.django_db
class TestDetailView:
    def test_detail_returns_person(self, client, guy):
        response = client.get(reverse('guys:detail', args=[guy.pk]))
        assert response.status_code == 200
        assert response.context['guy'].pk == guy.pk

    def test_detail_404_for_missing(self, client):
        response = client.get(reverse('guys:detail', args=[99999]))
        assert response.status_code == 404


@pytest.mark.django_db
class TestRandomView:
    def test_random_empty_db_returns_404(self, client):
        response = client.get(reverse('guys:random'))
        assert response.status_code == 404

    def test_random_returns_a_person(self, client, guy):
        response = client.get(reverse('guys:random'))
        assert response.status_code == 200
        assert response.context['guy'].pk == guy.pk
        assert response.context.get('is_random') is True

    def test_random_returns_different_people(self, client, many_people):
        """При наличии 10 человек в базе данных, множественные запросы
        не всегда должны возвращать один и тот же результат"""
        seen_ids = set()
        for _ in range(20):
            response = client.get(reverse('guys:random'))
            assert response.status_code == 200
            seen_ids.add(response.context['guy'].pk)
        # При 20 попытках из 10 записей должно получиться как минимум 2 разных результата
        assert len(seen_ids) > 1

    def test_random_is_not_cached(self, client, guy):
        response = client.get(reverse('guys:random'))
        cache_control = response.get('Cache-Control', '')
        assert 'no-cache' in cache_control or 'no-store' in cache_control or 'max-age=0' in cache_control


@pytest.mark.django_db
class TestLoadView:
    @responses.activate
    def test_load_via_post_creates_records(self, client, sample_api_records):
        responses.add(
            responses.GET,
            settings.RANDOMDATATOOLS_URL,
            json=sample_api_records,
            status=200,
        )
        response = client.post(reverse('guys:load'), {'count': 3})
        assert response.status_code == 302
        assert response.url == reverse('guys:index')
        from guys.models import Guy
        assert Guy.objects.count() == 3

    def test_load_rejects_get(self, client):
        response = client.get(reverse('guys:load'))
        assert response.status_code == 405

    def test_load_rejects_invalid_count(self, client):
        response = client.post(reverse('guys:load'), {'count': 'abc'})
        assert response.status_code == 302  # Редирект с сообщением об ошибке
        from guys.models import Guy
        assert Guy.objects.count() == 0

    def test_load_rejects_zero_or_negative(self, client):
        response = client.post(reverse('guys:load'), {'count': 0})
        assert response.status_code == 302
        from guys.models import Guy
        assert Guy.objects.count() == 0

    def test_load_rejects_over_limit(self, client):
        response = client.post(reverse('guys:load'), {'count': 10000})
        assert response.status_code == 302
        from guys.models import Guy
        assert Guy.objects.count() == 0

    @responses.activate
    def test_load_handles_api_error_gracefully(self, client):
        responses.add(
            responses.GET,
            settings.RANDOMDATATOOLS_URL,
            status=500,
        )
        response = client.post(reverse('guys:load'), {'count': 5})
        # Редирект должен сопровождаться сообщением об ошибке, а не кодом 500
        assert response.status_code == 302
        from guys.models import Guy
        assert Guy.objects.count() == 0
