from django.db import models

class Post(models.Model):
    title = models.CharField(max_length=100)
    contents = models.TextField(blank=True)
    create_date = models.DateTimeField(auto_now_add=True,null=True)
    update_date = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

    class Meta:
        ordering = ['-create_date']