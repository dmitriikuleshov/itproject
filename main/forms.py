from django import forms


class LinkForm(forms.Form):
    link = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'Ссылка на аккаунт...'}))
