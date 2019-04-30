from __future__ import absolute_import, division, print_function
__metaclass__ = type
import json
import requests
from ansible.module_utils.basic import AnsibleModule, json, env_fallback
from ansible.module_utils.urls import fetch_url
from ansible.module_utils._text import to_native, to_bytes, to_text

try:
    from json.decoder import JSONDecodeError
except ImportError:
    JSONDecodeError = ValueError

def viptela_argument_spec():
    return dict(host=dict(type='str', required=True, fallback=(env_fallback, ['viptela_HOST'])),
            user=dict(type='str', required=True, fallback=(env_fallback, ['viptela_USER'])),
            password=dict(type='str', required=True, fallback=(env_fallback, ['viptela_PASSWORD'])),
            validate_certs=dict(type='bool', required=False, default=False),
            timeout=dict(type='int', default=30)
    )

STANDARD_HTTP_TIMEOUT = 10
STANDARD_JSON_HEADER = {'Connection': 'keep-alive', 'Content-Type': 'application/json'}

class viptelaModule(object):

    def __init__(self, module, function=None):
        self.module = module
        self.params = module.params
        self.result = dict(changed=False)
        self.headers = dict()
        self.function = function
        self.cookies = None
        self.json = None

        # normal output
        self.existing = None

        # info output
        self.config = dict()
        self.original = None
        self.proposed = dict()
        self.merged = None

        # debug output
        self.filter_string = ''
        self.method = None
        self.path = None
        self.response = None
        self.status = None
        self.url = None
        self.params['force_basic_auth'] = True
        self.user = self.params['user']
        self.password = self.params['password']
        self.host = self.params['host']
        self.timeout = self.params['timeout']
        self.modifiable_methods = ['POST', 'PUT', 'DELETE']

        self.session = requests.Session()
        self.session.verify = self.params['validate_certs']

        self.login()

    def _fallback(self, value, fallback):
        if value is None:
            return fallback
        return value

    def login(self):
        try:
            response = self.session.post(
                url='https://{0}/j_security_check'.format(self.host),
                headers={'Content-Type': 'application/x-www-form-urlencoded'},
                data={'j_username': self.user, 'j_password': self.password},
                timeout=self.timeout
            )
        except requests.exceptions.RequestException as e:  # This is the correct syntax
            self.fail_json(msg=e, **result)

        if response.text.startswith('<html>'):
            self.fail_json(msg='Could not login to device, check user credentials.', **self.result)
        else:
            return response

    def request(self, url_path, method='GET', headers=STANDARD_JSON_HEADER, data=None, files=None):
        """Generic HTTP method for viptela requests."""

        self.method = method
        self.headers = headers
        self.url = 'https://{0}{1}'.format(self.host, url_path)

        response = self.session.request(method, self.url, headers=headers, files=files, data=data)

        self.status_code = response.status_code
        self.status = requests.status_codes._codes[response.status_code][0]

        if self.status_code >= 300 or self.status_code < 0:
            try:
                decoded_response = response.json()
                details = decoded_response['error']['details']
                error = decoded_response['error']['message']
                self.fail_json(msg='{0}: {1}'.format(error, details))
            except JSONDecodeError as e:
                self.fail_json(msg=self.status)



        return response

    def get_feature_templates(self, factory_default=False, key_name='templateName'):
        response = self.request('/dataservice/template/feature')

        template_list = response.json()

        feature_templates = {}
        for template in template_list['data']:
            if factory_default == False and template['factoryDefault'] == 'true':
                continue
            key = template.pop(key_name)
            feature_templates[key] = template
            feature_templates[key]['templateDefinition'] = json.loads(template['templateDefinition'])
            feature_templates[key]['editedTemplateDefinition'] = json.loads(template['editedTemplateDefinition'])

        return feature_templates

    def get_device_templates(self, system_created=False, key_name='templateName'):
        device_response = self.request('/dataservice/template/device')

        device_body = device_response.json()

        feature_templates = self.get_feature_templates(factory_default=True, key_name='templateId')

        device_templates = {}
        for device in device_body['data']:
            object_response = self.request('/dataservice/template/device/object/{0}'.format(device['templateId']))
            object = object_response.json()
            key = object.pop(key_name)
            device_templates[key] = object

            if 'generalTemplates' in object:
                generalTemplates = []
                for template in object.pop('generalTemplates'):
                    if 'subTemplates' in template:
                        subTemplates = []
                        for sub_template in template['subTemplates']:
                            subTemplates.append({'templateName':feature_templates[sub_template['templateId']]['templateName'], 'templateType':sub_template['templateType']})
                        template_item = {'templateName': feature_templates[template['templateId']]['templateName'],
                                         'templateType': template['templateType'],
                                         'subTemplates': subTemplates}
                    else:
                        template_item = {'templateName': feature_templates[template['templateId']]['templateName'],
                                         'templateType': template['templateType']}
                    generalTemplates.append(template_item)


                device_templates[key]['generalTemplates'] = generalTemplates

        return device_templates

    def exit_json(self, **kwargs):
        """Custom written method to exit from module."""
        self.result['status'] = self.status
        self.result['status_code'] = self.status_code
        self.result['url'] = self.url
        self.result['method'] = self.method

        self.result.update(**kwargs)
        self.module.exit_json(**self.result)

    def fail_json(self, msg, **kwargs):
        """Custom written method to return info on failure."""
        self.result['status'] = self.status
        self.result['status_code'] = self.status_code
        self.result['url'] = self.url
        self.result['method'] = self.method

        self.result.update(**kwargs)
        self.module.fail_json(msg=msg, **self.result)