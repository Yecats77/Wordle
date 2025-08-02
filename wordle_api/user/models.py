from django.db import models
from django.contrib.postgres.fields import HStoreField
from django.contrib.postgres.fields import ArrayField

class user(models.Model):
    id = models.AutoField(primary_key=True) # user id
    opponent_id = models.IntegerField() # opponent user.id, None if game_type is not multi-player
    game_id = models.IntegerField() # game.id

    class Meta:
        db_table = 'user'
        verbose_name = 'user'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.id
