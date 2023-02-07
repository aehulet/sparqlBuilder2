from django.shortcuts import render
from .models import Topic, Item
from . import dbmgmt
import re


def index(request):
    dbmgmt.get_topic_data(True)
    topic_results = Topic.objects.all()
    context = {'topic_results': topic_results}
    return render(request, 'unlv/index.html', context)


def item(request, item_id):
    dbmgmt.get_item_data(item_id)
    item_results = Item.objects.filter(topic_id__exact=item_id)
    context = {'item_results': item_results}
    return render(request, 'unlv/item.html', context)
