from django.db import models

class PageContent(models.Model):
    name = models.CharField(max_length=50)
    banner_img = models.ImageField(upload_to='pages/', blank=True)
    banner_img_description = models.CharField(max_length=100, blank=True)
    body = models.TextField()

    def __str__(self):
        return self.name