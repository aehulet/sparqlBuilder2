from django.shortcuts import render
from django.http import HttpResponse
from .models import Topic, Item
from .dbmgmt import get_topic_data


def index(request):
    get_topic_data(True)
    topic_results = Topic.objects.all()
    context = {'topic_results': topic_results}
    return render(request, 'unlv/index.html', context)


def item(request, item_id):
    return HttpResponse("This is for the item details.")
