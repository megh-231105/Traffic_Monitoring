# traffic_app/forms.py
from django import forms
from .models import VideoUpload

class VideoUploadForm(forms.ModelForm):
    class Meta:
        model = VideoUpload
        fields = ["title", "video_file"]
        widgets = {
            "title": forms.TextInput(attrs={"class":"form-control", "placeholder":"Optional title"}),
            "video_file": forms.ClearableFileInput(attrs={"class":"form-control-file"})
        }
