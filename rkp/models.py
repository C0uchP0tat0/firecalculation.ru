from django.db import models
from django.dispatch import receiver
from django.db.models.signals import post_save, post_delete
from django.contrib.auth.models import User


class FireLoad(models.Model):
    material = models.CharField(max_length=4096, verbose_name='Материал')
    heat = models.FloatField(
        null=True, verbose_name='Низшая теплота сгорания МДж/кг')
    user = models.ForeignKey(
        User, on_delete=models.PROTECT, blank=True, null=True)

    def __str__(self):
        return self.material


class FireObject(models.Model):
    title = models.CharField(
        max_length=4096,
        verbose_name='Название объекта')
    length = models.FloatField(null=True, verbose_name='Длина, м')
    width = models.FloatField(null=True, verbose_name='Ширина, м')
    height = models.FloatField(
        null=True,
        verbose_name='Растояние от пожарной нагрузки до нижнего пояса ферм, м')
    result = models.FloatField(blank=True, null=True, verbose_name='Площадь')
    q_sum = models.FloatField(blank=True, null=True,
                              verbose_name='Суммареая пожарная нагрузка МДж')
    production_category = models.CharField(
        blank=True, max_length=10, verbose_name='Категория производств')
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, blank=True, null=True)

    def __str__(self):
        return self.title


class Quantity(models.Model):
    weight = models.FloatField(null=True, verbose_name='Колличество кг')
    material_Q = models.FloatField(
        blank=True,
        null=True,
        verbose_name='Пожарная нагрузка МДж'
    )
    fire_load = models.ForeignKey(
        FireLoad,
        on_delete=models.CASCADE,
        blank=True,
        null=True
    )
    fire_object = models.ForeignKey(
        FireObject,
        on_delete=models.CASCADE,
        blank=True,
        null=True
    )

    def __str__(self):
        return str(self.weight)


@receiver(post_save, sender=FireObject, weak=False)
def update_calculated_fields(sender, instance, **kwargs):
    result = instance.length * instance.width
    sender.objects.filter(pk=instance.pk).update(result=result)


@receiver(post_save, sender=Quantity, weak=False)
def get_id(sender, instance, **kwargs):

    try:
        # проверяем все ли поля заполнены
        if instance.fire_load is None or instance.weight is None:
            # если хоть одно поле пустое, удаляем объект
            sender.objects.filter(pk=instance.pk).delete()
            return (rkp(instance=instance))
        else:
            # вычисляем поле пожарная нагрузка
            fire_load = instance.fire_load.id
            load = FireLoad.objects.get(id=fire_load).heat
            material_Q = instance.weight * load
            sender.objects.filter(pk=instance.pk).update(material_Q=material_Q)
        rkp(instance=instance)
        print(instance)
    except AttributeError:
        return sender


@receiver(post_delete, sender=Quantity, weak=False)
def get_id_del(sender, instance, **kwargs):
    try:
        rkp(instance=instance)
    except:
        return instance


def rkp(instance):
    fire_object = FireObject.objects.get(id=instance.fire_object.id)
    materials_Q = Quantity.objects.filter(fire_object=fire_object)
    Q_res = 0
    for Q in materials_Q:
        Q_res = Q_res + Q.material_Q
    Q_SUM = Q_res/fire_object.result
    production_category = 'В4'
    if Q_SUM <= 180:
        production_category = 'В4'
    elif 181 <= Q_SUM <= 1400:
        Q_OBJ = 0.64 * 1400 * fire_object.height**2
        if Q_res >= Q_OBJ:
            production_category = 'В2'
        else:
            production_category = 'В3'
    elif 1401 <= Q_SUM <= 2200:
        Q_OBJ = 0.64 * 2200 * fire_object.height**2
        if Q_res >= Q_OBJ:
            production_category = 'В1'
        else:
            production_category = 'В2'
    elif 2201 <= Q_SUM:
        production_category = 'В1'

    FireObject.objects.filter(
        id=instance.fire_object.id).update(
            production_category=production_category, q_sum=Q_SUM)
