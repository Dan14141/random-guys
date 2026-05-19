import pytest

from guys.services import guy_from_api_dict

@pytest.mark.django_db
class TestGuyModel:
    def test_create_person(self, guy):
        assert guy.pk is not None
        assert str(guy) == 'Некрестьянова Василиса'

    def test_get_gender_display(self, guy):
        assert guy.get_gender_display() == 'Женщина'

    def test_from_api_dict_maps_fields(self, sample_api_record):
        g = guy_from_api_dict(sample_api_record)
        assert g.gender == 'woman'
        assert g.first_name == 'Василиса'
        assert g.last_name == 'Некрестьянова'
        assert g.phone == '+7 (937) 301-49-94'
        assert g.email == 'vasilisa1961@yandex.ru'
        assert g.address.startswith('Россия')

    def test_from_api_dict_handles_missing_keys(self):
        g = guy_from_api_dict({})
        assert g.gender == ''
        assert g.first_name == ''
        assert g.email == ''
