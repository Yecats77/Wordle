from django.db import models
from django.contrib.postgres.fields import HStoreField
from django.contrib.postgres.fields import ArrayField

class game(models.Model):
    id = models.AutoField(primary_key=True) # game id
    game_type = models.CharField(max_length=20) # server/client, host cheating, multi-player
    game_param = HStoreField() # max_round, word_list
    game_score = models.IntegerField(default=0)
    game_state = models.CharField(max_length=20)  
    submitted_words = ArrayField(models.CharField(max_length=5))

    class Meta:
        db_table = 'game'
        verbose_name = 'game'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.id
