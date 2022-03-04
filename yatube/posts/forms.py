from django import forms

from .models import Post, Comment


class PostForm(forms.ModelForm):
    def clean_text(self):
        data = self.cleaned_data["text"]
        if not data:
            raise forms.ValidationError("Пост не может быть пустым!")
        return data

    class Meta:
        model = Post
        fields = ("text", "group", "image")
        label = {'image': 'Картинка'}


class CommentForm(forms.ModelForm):
    def clean_text(self):
        data = self.cleaned_data["text"]
        if not data:
            raise forms.ValidationError("поле Text не должно быть пустым")
        return data

    class Meta:
        model = Comment
        fields = ("text",)
