from . import spql
from .models import Topic, Item


def get_topic_data(reload: bool):
    # loads wikidata base query for topics into local db
    if reload:
        funct_val = False
        t = Topic.objects.all()
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
