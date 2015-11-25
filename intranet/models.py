# -*- coding: utf-8 -*-
from django.db import models

class MetaModelPlus(models.base.ModelBase):
    def __new__(cls, name, bases, attrs):
        my_meta = super(MetaModelPlus, cls).__new__(cls, name, bases, attrs)
        my_meta._meta.permissions.append(('view_' + my_meta._meta.module_name, u'Can view %s' % my_meta._meta.verbose_name),)
        return my_meta

class ModelPlus(models.Model):
    class Meta(MetaModelPlus):
        abstract = True