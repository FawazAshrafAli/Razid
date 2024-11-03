from django import forms
from . models import Customer
from django.contrib.auth.forms import SetPasswordForm,PasswordResetForm
from .models import Customer
from django.core.mail import send_mail
from django.utils.crypto import get_random_string



class CustomerProfileForm(forms.ModelForm):
    class Meta:
        model=Customer
        fields=['name','locality','city','mobile','state','zipcode']
        widgets={
            'name':forms.TextInput(attrs={'class':'form-control'}),
            'locality':forms.TextInput(attrs={'class':'form-control'}),
            'city':forms.TextInput(attrs={'class':'form-control'}),
            'mobile':forms.NumberInput(attrs={'class':'form-control'}),
            'state':forms.Select(attrs={'class':'form-control'}),
            'zipcode':forms.NumberInput(attrs={'class':'form-control'}),

        }



class MyPasswordResetForm(PasswordResetForm):
    email=forms.EmailField(widget=forms.EmailInput(attrs={'class':'form-control'}))
    def send_mail(self, subject_template_name, email_template_name, context, from_email, to_email, html_email_template_name=None):
        otp = get_random_string(length=6, allowed_chars='1234567890')

        # Add OTP to the email context
        context['otp'] = otp

        # Send OTP through email
        send_mail(subject_template_name, email_template_name, context, from_email, [to_email])

        # Call the parent class method to send the password reset email
        super().send_mail(subject_template_name, email_template_name, context, from_email, to_email, html_email_template_name)


class MySetPasswordForm(SetPasswordForm):
    new_password1=forms.CharField(label='New Password',widget=forms.PasswordInput(attrs={'autocomplete':'current-password','class':'form-control'}))
    new_password2=forms.CharField(label='Confirm New Password',widget=forms.PasswordInput(attrs={'autocomplete':'current-password','class':'form-control'}))
    