
from django.db import models
from django.core.serializers.json import DjangoJSONEncoder
from django.utils import simplejson
from django.contrib.contenttypes.models import ContentType


class ContentTypeJSONEncoder(DjangoJSONEncoder):
    def default(self, obj):
        if isinstance(obj, models.Model):
            # `default` must return a python serializable structure
            ct = ContentType.objects.get_for_model(obj)
            return {
                '__model__' : ct.model,
                '__app_label__' : ct.app_label,
                'id' : obj.id,
                }
        else:
            return super(ContentTypeJSONEncoder, self).default(obj)


class ContentTypeJSONDecoder(simplejson.JSONDecoder):
    def __init__(self, **kwargs):
        kwargs.pop('object_hook', None)
        simplejson.JSONDecoder.__init__(self, object_hook=self.dict_to_object, **kwargs)

    def dict_to_object(self, d):
        try:
            model = d.get('__model__')
            app_label = d.get('__app_label__')
            id = d.get('id')

            model_type = ContentType.objects.get(app_label=app_label, model=model)
            return model_type.get_object_for_this_type(id=id)
        except:
            return d
