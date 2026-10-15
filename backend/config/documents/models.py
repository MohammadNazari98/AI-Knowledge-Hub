from django.db import models
from django.contrib.auth.models import User
from knowledge_bases.models import KnowledgeBase
from pathlib import Path
from django.core.exceptions import ValidationError


class Document(models.Model):
    class Status(models.TextChoices):
        UPLOADED = "فایل آپلود شده."
        PROCESSING = "استخراج متن درحال انجام است.",
        PROCESSED = "استخراج متن موفق بوده."
        FAILED = "پردازش ناموفق بوده."
    
    class FileType(models.TextChoices):
        TXT = "txt", "Text"
        PDF = "pdf", "PDF"
    
    title = models.CharField(max_length=100)
    knowledge_base = models.ForeignKey(KnowledgeBase, related_name="documents", on_delete=models.CASCADE)
    file = models.FileField(upload_to="documents/")
    file_type = models.CharField(max_length=4, choices=FileType.choices)
    status = models.CharField(max_length=30, choices=Status.choices, default=Status.UPLOADED)
    content = models.TextField(blank=True, default="")
    created_by = models.ForeignKey(User, related_name="documents", on_delete=models.PROTECT)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.title
    
    def clean(self):
        super().clean()
        if self.file:
            extension = Path(self.file.name).suffix.lower().lstrip(".")
            if extension != self.file_type:
                raise ValidationError({
                    "The file type does not match the file extension."
                })
                
    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["knowledge_base", "title"], name="unique_document_title_per_knowledge_base")
        ]