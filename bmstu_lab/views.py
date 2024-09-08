from django.http import HttpResponse
from django.shortcuts import render, redirect
from datetime import date
def hello(request):
    return render(request,"index.html",
                  {"data":{"current_date" : date.today(),
                           'list': ['python','Dota 2', 'deadlock']
                           }})

def GetOrders(request):
    return render(request, 'orders.html', {'data' : {
        'current_date': date.today(),
        'orders': [
            {'title': 'Книга с картинками', 'id': 1},
            {'title': 'Бутылка с водой', 'id': 2},
            {'title': 'Коврик для мышки', 'id': 3},
        ]
    }})

def GetOrder(request, id):
    return render(request, 'order.html', {'data' : {
        'current_date': date.today(),
        'id': id
    }})


def sendText(request):
    if request.method == 'POST':
        input_text = request.POST['text']
        return HttpResponse(f"Вы ввели: {input_text}")
    else:
        return redirect('')