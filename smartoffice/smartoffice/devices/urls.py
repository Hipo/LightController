from django.conf.urls import url
from smartoffice.devices.views import ListDevicesView, SwitchDetailView, ListSwitchesView, DeviceDetailView


urlpatterns = [
    url(r'^devices/$', ListDevicesView.as_view(), name='list-devices'),
    url(r'^devices/(?P<device_id>[0-9A-Za-z-]+)/switches/$', ListSwitchesView.as_view(), name='list-device-switches'),
    url(r'^devices/initialize/$', DeviceDetailView.as_view(), name='device-detail'),
    url(r'^switches/(?P<switch_id>[0-9A-Za-z-]+)/$', SwitchDetailView.as_view(), name='switch-detail'),
]