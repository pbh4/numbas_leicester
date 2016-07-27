from django.http import HttpResponse
from channels.handler import AsgiHandler
from channels import Group
from channels.sessions import channel_session,enforce_ordering
from channels.auth import http_session_user, channel_session_user, channel_session_user_from_http
from channels.generic import BaseConsumer
import json

from django.contrib.auth.models import User

from .models import Attempt,ScormElement,Resource, ReportProcess
from .report_outcome import report_outcome

@enforce_ordering(slight=True)
@channel_session_user_from_http
def scorm_connect(message,pk):
    pass

@channel_session_user
def scorm_set_element(message,pk):
    data = json.loads(message.content['text'])
    for element in data:
        attempt = Attempt.objects.get(pk=pk)
        ScormElement.objects.create(
            attempt = attempt,
            key = element['key'], 
            value = element['value']
        )

def report_scores(message,**kwargs):
    resource = Resource.objects.get(pk=message['pk'])
    process = ReportProcess.objects.create(resource=resource)
    for user in User.objects.filter(attempts__resource=resource).distinct():
        request = report_outcome(resource,user)
        if request.status_code != 200:
            process.status = 'error'
            process.response = request.text
            process.save()
            return
    process.status = 'complete'
    process.save()