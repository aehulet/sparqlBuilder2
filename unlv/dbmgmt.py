from . import spql
from unlv import models


def get_topic_data(reload: bool):
    # loads wikidata base query for topics into local db
    if reload:
        funct_val = False
        t = models.Topic.objects.all()
        if t:
            t.delete()
    try:
        qry = spql.get_wd_query(spql.LOAD_BASE)
        latest_result = spql.load_base(qry)
        for i in latest_result:
            new = models.Topic.objects.create(topic_id=i[0], topic_text=i[1], category=i[2])
        funct_val = True
    except IndexError as ie:
        return "error:Qcode already inserted"

    return funct_val


def get_item_data(qcode):
    funct_val = False
    # create nested results list from SPARQL query: works
    qry = spql.query_item_detail(qcode)
    result_dict = spql.get_wd_query(qry)
    item_results = spql.load_item_detail(result_dict)

    # instantiate a QuerySet of existing Items
    objs = models.Item.objects.filter(topic_id=qcode)
    objs.delete()

    for i in item_results:
        new = models.Item(topic_id=i[0], item_text=i[1], item_property=i[2], item_value=i[3])
        new.save(force_insert=True)
    funct_val = True
    return funct_val


def test_item():
    s = ''
    the_obj = models.Item.objects.all()
    for o in the_obj:
        s = o.topic_id
    return s + " from Item"
