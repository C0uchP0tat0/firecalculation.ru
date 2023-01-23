from django import forms
from .models import FireObject, FireLoad, Quantity
# from django.dispatch import receiver
# from django.db.models.signals import post_save
# from django.forms.formsets import formset_factory
# from django.forms import PasswordInput, modelformset_factory


class FireLoadChoiceField(forms.ModelMultipleChoiceField, forms.FloatField):

    weight = forms.FloatField()

    def label_from_instance(self, obj):
        return f'{obj.material} - {obj.heat}'


class WeightForm(forms.Form):
    queryset = FireLoad.objects.all()
    fire_load = forms.ModelChoiceField(queryset=queryset)
    weight = forms.CharField()


class FireObjectForm(forms.ModelForm):

    class Meta:
        model = FireObject
        fields = ['title', 'length', 'width', 'height', 'user']
        widgets = {'user': forms.HiddenInput(), }

    '''def __init__(self, *args, **kwargs):
        super(FireObjectForm, self).__init__(*args, **kwargs)
        self.weightFormset =  formset_factory(
            WeightForm,
            extra=self.queryset.count())
        self.weights = self.weightFormset()'''


class QuantityForm(forms.ModelForm):
    weight = forms.FloatField(required=False, label='Колличество кг')

    class Meta:

        model = Quantity

        # fields = '__all__'
        fields = ['fire_load', 'weight', 'fire_object']
        widgets = {'fire_object': forms.HiddenInput(), }

    def __init__(self, user, *args, **kwargs):
        super(QuantityForm, self).__init__(*args, **kwargs)
        self.fields['fire_load'].queryset = FireLoad.objects.filter(
            user=user.id)

    '''def clean(self):
        cleaned_data = super().clean()
        fire_load = cleaned_data.get("fire_load")
        weight = cleaned_data.get("weight")

        if (weight or fire_load) is None:
            msg = "Необходимо что бы хотя бы одно поле было заполнено."
            self.add_error('weight', msg)
            self.add_error('fire_load', msg)'''


class UserForm(forms.Form):
    username = forms.CharField()
    password = forms.CharField(widget=forms.PasswordInput())


class FireloadCreateForm(forms.ModelForm):

    class Meta:

        model = FireLoad

        fields = ['material', 'heat', 'user']
        widgets = {'user': forms.HiddenInput(), }
