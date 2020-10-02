from django.db import models

from django.contrib.auth import get_user_model
User = get_user_model()

class Question(models.Model):
    question_text = models.TextField()
    correct_ans = models.CharField(max_length=200, default='')
    mark = models.FloatField(default=0.0)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    
    def __str__(self):
        return self.question_text


class Choice(models.Model):
    choice = models.CharField(max_length=200)
    is_checked = models.CharField(max_length=100, default='unchecked')
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.choice 


class SelectedAnswer(models.Model):
    is_checked = models.CharField(max_length=100, default='unchecked')
    choice = models.ForeignKey(Choice, on_delete=models.CASCADE)
