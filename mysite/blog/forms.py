from django import forms
from .models import Comment

class EmailPostForm(forms.Form):
    name = forms.CharField(max_length=25)
    email = forms.EmailField()
    to = forms.EmailField()
    comments = forms.CharField(required=False, widget = forms.Textarea)

class CommentForm(forms.ModelForm): # 댓글을 달 수 있도록 작성
    class Meta:
        model = Comment
        fields = ['name', 'email', 'body']