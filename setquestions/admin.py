from django.contrib import admin
from .models import Choice, Question, SelectedAnswer


class ChoiceInline(admin.StackedInline):
    list_display = ('choice', 'is_checked',)     
    model = Choice
    extra = 3

@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ('user', 'question_text', 'correct_ans', 'mark',)    
    
    fieldsets = [
    (None,
    {'fields': ['user', 'question_text', 'correct_ans', 'mark']}),
    ]
    inlines = [ChoiceInline]


@admin.register(SelectedAnswer)
class SelectedAnswerAdmin(admin.ModelAdmin):
    list_display = ('choice', 'is_checked',) 


