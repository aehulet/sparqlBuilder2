from django.shortcuts import render
from .models import Topic, Item
from . import dbmgmt, session
import re

session_queries = []
query_count = 0


def index(request):
    dbmgmt.get_topic_data(True)
    topic_results = Topic.objects.all().order_by('topic_id', 'category')
    context = {'topic_results': topic_results}
    return render(request, 'unlv/index.html', context)


def item(request, item_id):
    # get item data from wikidata
    dbmgmt.get_item_data(item_id)
    global session_queries
    item_results = Item.objects.filter(topic_id__exact=item_id)
    global query_count
    query_count += 1
    qry = session.QueryRecord(item_id, 'item details for ' + item_results[0].item_text)
    qry.set_index(query_count)
    session_queries.append(qry)

    # insert data sets into context
    context = {'item_results': item_results, 'queries': session_queries}
    return render(request, 'unlv/item.html', context)
