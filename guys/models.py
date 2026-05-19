from django.db import models

class Guy(models.Model):
    """Модель для хранения информации о человеке"""
    GENDER_CHOICES = (('man', 'Мужчина'),('woman', 'Женщина'))
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES, verbose_name="Пол")
    first_name = models.CharField(max_length=30, verbose_name="Имя")
    last_name = models.CharField(max_length=30, verbose_name="Фамилия")
    phone = models.CharField(max_length=20, verbose_name="Номер телефона")
    email = models.EmailField(verbose_name="Электронная почта")
    address = models.CharField(max_length=255, verbose_name="Адрес")

    def __str__(self):
        """Строковое представление объекта: фамилия имя"""
        return f"{self.last_name} {self.first_name}"