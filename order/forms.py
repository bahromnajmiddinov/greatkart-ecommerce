from django import forms

from .models import Address, ContactInfo


class AddressForm(forms.ModelForm):
    class Meta:
        model = Address
        fields = ['address_line1', 'address_line2', 'city','state', 'zip_code', 'country']
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs.update({'class': 'form-control'})
            
    
class ContactInfoForm(forms.ModelForm):
    class Meta:
        model = ContactInfo
        fields = ['first_name', 'last_name', 'email', 'phone_number']
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs.update({'class': 'form-control'})
    
    def clearn_phone_number(self):
        phone_number = self.cleaned_data.get('phone_number')
        allowed_chars = '+0123456789'
        if phone_number and not all(char in allowed_chars for char in phone_number):
            raise forms.ValidationError('Invalid phone number')
        return phone_number
