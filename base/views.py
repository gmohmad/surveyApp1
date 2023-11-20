from django.shortcuts import render, redirect, get_object_or_404
from django.core.paginator import Paginator

from .models import Question, Answer

from .utils import calculate_the_stats


# Create your views here.


def start(request):
    if request.method == 'POST':
        ans = Answer.objects.create()

        if request.POST.get('choice'):
            ans.m_or_f = request.POST.get('choice')
            ans.save()
            return redirect('questions', 1, ans.id)

    return render(request, 'base/start.html', {})


def questions(request, pk, ans_pk):
    q = Question.objects.all()
    paginator = Paginator(q, 1)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    answers_len = 0
    if request.method == 'POST':

        if request.POST.get('choice'):
            ans = get_object_or_404(Answer, pk=ans_pk)
            question = get_object_or_404(Question, pk=pk)


            ans.answers[question.id] = request.POST.get('choice')
            ans.save()
            
            answers_len = len(ans.answers)

            if answers_len >= q.count():
                return redirect('result', ans_pk)

    context = {
        'page_obj': page_obj,
        'answers_len': answers_len + 1,
        'q_len': q.count(),
        'answerId': ans_pk
    }
    return render(request, 'base/question.html', context)


def stats(request):
    if not request.user.is_superuser:
        return redirect('start')
    else:
        all = calculate_the_stats(Answer.objects.all())
        ms = calculate_the_stats(Answer.objects.filter(m_or_f='A'))
        ws = calculate_the_stats(Answer.objects.filter(m_or_f='B'))
        context = {
            'all': all,
            'ms': ms,
            'ws': ws
        }
    return render(request, 'base/stats.html', context)


def result(request, pk):
    count = 0
    rez = ''
    ans = Answer.objects.get(id=pk)
    for i in ans.answers.values():
        if i == "A":
            count += 1
    if count < len(ans.answers) / 2:
        rez = 'У вас есть признаки депрессии'
    elif count == len(ans.answers) / 2:
        rez = 'Вам стоит провериться.'
    else:
        rez = 'У вас нет признаков депрессии'
    return render(request, 'base/result.html', {'result': rez})
