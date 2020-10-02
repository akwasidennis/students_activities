from django.shortcuts import get_object_or_404, render
from django.http import HttpResponseRedirect, HttpResponse, JsonResponse
from django.urls import reverse
from .models import Question, Choice, SelectedAnswer


def setquestions(request):
    q = Question.objects.filter()
    selected_choice = Choice.objects.filter()

    marks_scored = sum([m.mark for m in q])
    context = {
        'question': q,
        'marks_scored': marks_scored,
        'selected_choice': selected_choice,
    }
    return render(request, 'setquestions/set_questions.html', context)


def save_choice(request, question_pk, choice_text):
    p = get_object_or_404(Question, pk=question_pk)
    selected_choice = p.choice_set.get(choice=choice_text)
    unselected_choice = p.choice_set.exclude(choice=selected_choice.choice)
    
    selected_ans = SelectedAnswer.objects.filter(choice__question=p)
    if not selected_ans.exists():
        sa = SelectedAnswer.objects.create(is_checked="checked", choice=selected_choice)
    else:
        get_selected_ans = SelectedAnswer.objects.get(choice__question=p)
        get_selected_ans.delete()
        sa = SelectedAnswer.objects.create(is_checked="checked", choice=selected_choice)

    cor_ans = p.correct_ans
    sel_ans = selected_choice.choice
    if cor_ans == sel_ans:
        p.mark = 1.0
        p.save()
    else:
        p.mark = 0.0
        p.save()

    selected_choice.is_checked = 'checked'
    selected_choice.save()

    for unsel in unselected_choice:
        unsel.is_checked = 'unchecked'
        unsel.save()
    return HttpResponseRedirect(reverse('set-questions'))