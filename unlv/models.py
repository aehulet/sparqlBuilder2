from django.db import models


class Topic(models.Model):
    topic_id = models.CharField(max_length=20)
    topic_text = models.CharField(max_length=200)
    category = models.CharField(max_length=100)

    def __str__(self):
        return self.topic_id


class Item(models.Model):
    topic_id = models.CharField(max_length=20)
    item_text = models.CharField(max_length=200)
    item_property = models.CharField(max_length=10)
    item_value = models.CharField(max_length=100)

    def __str__(self):
        return self.topic_id
