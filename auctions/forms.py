from django import forms

class CreateForm(forms.Form):
    name = forms.CharField(label='auction name',strip=False)
    detail = forms.CharField(label='detail')
    imgURL = forms.URLField(label='URL', required=False)
    starting = forms.IntegerField(label='init price', min_value=12)


