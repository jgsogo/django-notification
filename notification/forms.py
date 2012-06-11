from django import forms
from django.contrib.contenttypes.models import ContentType

from notification.fields import NoticeTypeMultipleChoiceField
from notification.models import NoticeType, ObservedItem

class NotificationForm(forms.Form):
    content_type = None
    object_id = None
    user = None
    already_observed = None

    notices = NoticeTypeMultipleChoiceField(queryset=NoticeType.objects.none(), widget=forms.CheckboxSelectMultiple(), required=False)

    def __init__(self, content_type, object_id, user, *args, **kwargs):
        self.content_type = content_type
        self.object_id = object_id
        self.user = user
        super(NotificationForm, self).__init__(*args, **kwargs)
        self.fields['notices'].queryset = NoticeType.objects.filter(content_type=self.get_content_type())
        self.already_observed = self.fields['notices'].queryset.filter(observeditem__object_id=object_id, observeditem__user=user)
        self.fields['notices'].initial = self.already_observed.values_list('id', flat=True)

    def get_signal_for_notice_type(self, notice_type):
        return 'post_save'

    def get_content_type(self):
        return self.content_type

    def save(self):
        now_observing = self.cleaned_data['notices']
        for notice in self.fields['notices'].queryset:
            if notice in now_observing and notice not in self.already_observed:
                print "add  %s" % notice
                obj = ObservedItem(notice_type=notice, user=self.user, object_id=self.object_id, signal=self.get_signal_for_notice_type(notice))
                obj.save()
            if notice not in now_observing and notice in self.already_observed:
                print "delete  %s" % notice
                ObservedItem.objects.get(notice_type=notice, user=self.user, object_id=self.object_id, signal=self.get_signal_for_notice_type(notice)).delete()
