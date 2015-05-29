import json

from django.http import HttpResponse
from django.shortcuts import get_object_or_404, get_list_or_404
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import View
import requests
from smartoffice.devices.models import Device, Switch


def _create_json_http_response(bundle, **kwargs):
    response = {
        'results': bundle
    }

    kwargs.update({
        'content_type': 'application/json'
    })

    return HttpResponse(json.dumps(response), **kwargs)


class ListDevicesView(View):

    def get(self, request, *args, **kwargs):
        queryset = Device.objects.all()

        device_bundle = list()
        for device in queryset:
            device_bundle.append({
                'id': device.device_id,
                'name': device.name,
            })

        return _create_json_http_response(device_bundle)


class DeviceDetailView(View):

    @csrf_exempt
    def dispatch(self, request, *args, **kwargs):
        return super(DeviceDetailView, self).dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        device_data = json.loads(request.POST.get('device_data'))

        device, created = Device.objects.get_or_create(device_id=device_data["device_uuid"])

        for switch_id in device_data["switches"]:
            Switch.objects.get_or_create(switch_id=switch_id, defaults={
                'device': device
            })

        return _create_json_http_response(True)


class ListSwitchesView(View):

    def get(self, request, *args, **kwargs):
        device = get_object_or_404(Device, device_id=kwargs.get('device_id'))

        switch_bundle = list()
        for switch in device.switches.all():
            switch_bundle.append({
                'id': switch.switch_id,
                'name': switch.name,
                'status': switch.status
            })

        return _create_json_http_response(switch_bundle)


class SwitchDetailView(View):

    @csrf_exempt
    def dispatch(self, request, *args, **kwargs):
        return super(SwitchDetailView, self).dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        switch = get_object_or_404(Switch, switch_id=kwargs.get('switch_id'))

        switch_bundle = {
            'id': switch.switch_id,
            'name': switch.name,
            'status': switch.status
        }

        return _create_json_http_response(switch_bundle)

    def post(self, request, *args, **kwargs):
        switch = get_object_or_404(Switch, switch_id=kwargs.get('switch_id'))

        request_body = json.loads(request.body)

        switch.status = request_body["status"]
        switch.save()

        post_url = 'http://127.0.0.1:8888/device/%s/message' % switch.device.device_id
        '''
        requests.post(post_url, data={
            'switch_id': switch.switch_id,
            'on_off': switch.status,
            'cmd': 'switch_light'
        })
        '''

        return _create_json_http_response(bool(int(switch.status)))
