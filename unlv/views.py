from django.shortcuts import render
from django.http import HttpResponse
from .models import Topic, Item
from .dbmgmt import get_topic_data, get_item_data
import re

def index(request):
    get_topic_data(True)
    topic_results = Topic.objects.all()
    context = {'topic_results': topic_results}
    return render(request, 'unlv/index.html', context)


def item(request, item_id):
    # hacky way to get item id
    elements = re.split(r'\/', request.path)
    q_code = elements.pop(1)

    get_item_data(q_code)
    item_results = Item.objects.get(fk_topic_id=q_code)
    context = {'item_results': item_results}
    return render(request, 'unlv/item.html', context)
