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
    url(r'^groups/$', api.ListGroups.as_view(), name='groups'),
    url(r'^lightsensor/$', api.ListLightSensor.as_view(), name='lightsensor'),
    url(r'^gpiodevices/$', api.ListGPIOOutputDevices.as_view(), name='gpiodevices'),
    url(r'^pioneerdevices/$', api.ListPioneerDevices.as_view(), name='pioneerdevices'),
    url(r'^gpiodeviceactions/$', api.ListGPIODeviceActions.as_view(), name='gpiodeviceactions'),
    url(r'^pioneerdeviceactions/$', api.ListPioneerDeviceActions.as_view(), name='pioneerdeviceactions'),
    url(r'^togglegpiodevice/$', api.ToggleGPIODevice.as_view(), name='togglegpiodevice'),
    url(r'^togglepioneerdevice/$', api.TogglePioneerDevice.as_view(), name='togglepioneerdevice'),
    url(r'^registernotificationclient/$', api.RegisterNotificationClient.as_view(), name='registernotificationclient'),
    url(r'^getauthtoken/$', api.GetAuthToken.as_view(), name='getauthtoken'),
    url(r'^togglealarm/$', api.ToggleAlarm.as_view(), name='togglealarm'),
    url(r'^getalarm/$', api.GetAlarm.as_view(), name='getalarm')
]