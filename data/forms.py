# from pyexpat import model
from dataclasses import fields
from .models import User_profile, Obj, System, Atributes, Data
from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm

class CreateUserForm(UserCreationForm):
        class Meta:
            model = User_profile
            fields = ('email',)
            # exclude=['created_at', 'updated_at'] 

class ChangeUserForm(UserChangeForm):
        class Meta:
            model = User_profile
            fields = ('email',)
            
class CreateObjForm(forms.ModelForm):
        class Meta:
            model = Obj
            exclude=['created_at', 'updated_at'] 
        def __init__(self, *args, **kwargs):
             super().__init__(*args, **kwargs)
             self.fields['user'].widget=forms.HiddenInput()

            
class CreateSystemForm(forms.ModelForm):
        class Meta:
            model = System
            exclude=['created_at', 'updated_at']
    
class CreateAtribForm(forms.ModelForm):
    class Meta:
        model = Atributes
        exclude=['created_at', 'updated_at', ] 


class WriteDataForm(forms.ModelForm):
     class Meta:
        model = Data
        fields = ['value',]


class CreateDataForm(forms.ModelForm):
    class Meta:
            model = Data
            exclude = '__all__'
    def __init__(self, *args, **kwargs):
        # Получаем pk из kwargs
        related_pk = kwargs.pop('atr_pk', None)
        super().__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[f'{field}'].widget.attrs['readonly'] = True
        
        # Устанавливаем значение по умолчанию для поля, если related_pk передан
        if related_pk:
            self.fields['name'].initial = related_pk 

