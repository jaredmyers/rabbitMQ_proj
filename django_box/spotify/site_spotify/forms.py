from django import forms

class RegisterForm(forms.Form):
    username = forms.CharField(label='User Name')
    pw = forms.CharField(label="Password")
    pw2 = forms.CharField(label="Retype Password")

class LoginForm(forms.Form):
    username = forms.CharField(label='User Name')
    pw = forms.CharField(label="Password")

class PostThread(forms.Form):
    threadname = forms.CharField(label="Thread Name:")
    threadcontent = forms.CharField(widget=forms.Textarea, label="Discussion:")

class PostReply(forms.Form):
    replycontent = forms.CharField(widget=forms.Textarea, label="reply")

class AddFriend(forms.Form):
    addfriend = forms.CharField(label="")

class SendChat(forms.Form):
    sendmessage = forms.CharField(label="")