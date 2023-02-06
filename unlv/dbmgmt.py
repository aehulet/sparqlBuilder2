from . import spql
from unlv import models


def get_topic_data(reload: bool):
    # loads wikidata base query for topics into local db
    if reload:
        funct_val = False
        t = models.Topic.objects.all()
        if t:
            t.delete()
            t.update()

        qry = spql.get_wd_query(spql.LOAD_BASE)
        latest_result = spql.load_base(qry)
        for i in latest_result:
            new = t.create()
            new.topic_id = i[0]
            new.topic_text = i[1]
            new.category = i[2]
            new.save()
        funct_val = True

        return funct_val


def get_item_data(qcode):
    funct_val = False
    qry = spql.query_item_detail(qcode)
    result_dict = spql.get_wd_query(qry)
    item_results = spql.load_item_detail(result_dict)

    i_objs = models.Item.objects.get(fk_topic_id=qcode)

    # if i_objs:
    #    i_objs.delete()
    #    i_objs.update()
    for i in item_results:
        new = i_objs.create()
        new.fk_topic_id = i[0]
        new.item_text = i[1]
        new.item_property = i[2]
        new.item_value = i[3]
        new.save()
    funct_val = True
    return funct_val


def test_item():
    the_obj = models.Topic.objects.all()
    for o in the_obj:
        s = o.topic_id
    return s

