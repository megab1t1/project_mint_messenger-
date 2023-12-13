from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse


class Messages(models.Model):
    message = models.TextField()
    send_time = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(User, db_index=True, on_delete=models.CASCADE, related_name='user')
    user_to = models.ForeignKey(User, db_index=True, on_delete=models.CASCADE, related_name='user_to')
    is_read = models.BooleanField(default=False)

    class Meta:
        ordering = ('send_time', 'message')

    def get_absolute_url_edit(self):
        return reverse('edit', kwargs={'user': User.objects.get(id=self.user_to_id).id,
                                       'message': self.pk})

    def get_absolute_url_delete(self):
        return reverse('delete', kwargs={'message': self.pk})
