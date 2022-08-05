from django.conf.urls import url
import automation.api as api
from django.views.generic.base import TemplateView
from django.contrib.auth.decorators import login_required
from django.contrib.auth import views as auth_views

app_name = 'automation'

urlpatterns = [
    url(r'^$', login_required(TemplateView.as_view(template_name='automation/index.html'))),
    url(r'^accounts/login/$', auth_views.LoginView.as_view(), name='login'),
    url(r'^logout/$', auth_views.LogoutView.as_view(),{'next_page': '/accounts/login'}),
    url(r'^actions/$', api.GetActions.as_view(), name='actions'),
    url(r'^actionshistory/$', api.GetActionsHistory.as_view(), name='actions'),
    url(r'^executeaction/$', api.ExecuteAction.as_view(), name='executeaction'),
    url(r'^togglealarm/$', api.ToggleAlarm.as_view(), name='togglealarm'),
    url(r'^alarm/$', api.GetAlarm.as_view(), name='alarm'),
    url(r'^media/$', api.GetMedia.as_view(), name='media'),
    url(r'^deletemedia/$', api.DeleteMedia.as_view(), name='deletemedia'),
    url(r'^playmusic/$', api.PlayMusic.as_view(), name='playmusic'),
    url(r'^systemstatus/$', api.SystemStatus.as_view(), name='systemstatus')
]