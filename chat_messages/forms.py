# messages/forms.py
from django import forms
from .models import Comment, PrivateMessage

class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['content']
        widgets = {
            'content': forms.Textarea(
                attrs={'rows': 3, 'class': 'form-control', 'placeholder': '对商品有什么疑问？问问卖家吧...'}),        }

class PrivateMessageForm(forms.ModelForm):
    class Meta:
        model = PrivateMessage
        fields = ['content']
        widgets = {
            'content': forms.Textarea(attrs={'rows': 4}),
        }