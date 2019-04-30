#!/usr/bin/python

ANSIBLE_METADATA = {
    'metadata_version': '1.1',
    'status': ['preview'],
    'supported_by': 'community'
}

DOCUMENTATION = '''
---
module: viptela_package

short_description: This is my sample module

version_added: "2.4"

description:
    - "This is my longer description explaining my sample module"

options:
    name:
        description:
            - The name of the package
        required: true
    state:
        description:
            - The state if the bridge ('present' or 'absent') (Default: 'present')
        required: false
    file:
        description:
            - The file name of the package
        required: false

author:
    - Steven Carter
'''

EXAMPLES = '''
# Upload and register a package
- name: Package
  viptela_package:
    host: 1.2.3.4
    user: admin
    password: cisco
    file: asav.tar.gz
    name: asav
    state: present

# Deregister a package
- name: Package
  viptela_package:
    host: 1.2.3.4
    user: admin
    password: cisco
    name: asav
    state: absent
'''

RETURN = '''
original_message:
    description: The original name param that was passed in
    type: str
message:
    description: The output message that the sample module generates
'''

import requests
from ansible.module_utils.basic import AnsibleModule, json
from ansible.module_utils.viptela import viptelaModule, viptela_argument_spec


def run_module():
    # define available arguments/parameters a user can pass to the module
    argument_spec = viptela_argument_spec()
    argument_spec.update(state=dict(type='str', choices=['absent', 'present'], default='present'),
                         name = dict(type='str', alias='templateName'),
                         description = dict(type='str', alias='templateDescription'),
                         definition = dict(type='str', alias='templateDefinition'),
                         type = dict(type='str', alias='templateType'),
                         device_type = dict(type='list', alias='deviceType'),
                         template_min_version = dict(type='str', alias='templateMinVersion'),
                         factory_default=dict(type='bool', alias='factoryDefault'),
                         aggregate=dict(type='dict'),
    )

    # seed the result dict in the object
    # we primarily care about changed and state
    # change is if this module effectively modified the target
    # state will include any data that you want your module to pass back
    # for consumption, for example, in a subsequent task
    result = dict(
        changed=False,
    )

    # the AnsibleModule object will be our abstraction working with Ansible
    # this includes instantiation, a couple of common attr would be the
    # args/params passed to the execution, as well as if the module
    # supports check mode
    module = AnsibleModule(argument_spec=argument_spec,
                           supports_check_mode=True,
                           )
    viptela = viptelaModule(module)

    # if the user is working with this module in only check mode we do not
    # want to make any changes to the environment, just return the current
    # state with no modifications
    if module.check_mode:
        return result

    feature_templates = viptela.get_feature_templates(factory_default=True)
    device_templates = viptela.get_device_templates()

    if viptela.params['aggregate']:
        if viptela.params['state'] == 'present':
            for name, data in viptela.params['aggregate'].items():
                if name not in device_templates:
                    payload = {}
                    payload['templateName'] = name

                    payload['templateDescription'] = data['templateDescription']
                    payload['deviceType'] = data['deviceType']
                    payload['factoryDefault'] = data['factoryDefault']
                    payload['configType'] = data['configType']
                    if data['configType'] == 'file':
                        payload['templateConfiguration'] = data['templateConfiguration']
                        viptela.request('/dataservice/template/device/cli', method='POST', data=json.dumps(payload))
                    else:
                        generalTemplates = []
                        for template in data['generalTemplates']:
                            if 'subTemplates' in template:
                                subTemplates = []
                                for sub_template in template['subTemplates']:
                                    subTemplates.append(
                                        {'templateId': feature_templates[sub_template['templateName']]['templateId'],
                                         'templateType': sub_template['templateType']})
                                template_item = {
                                    'templateId': feature_templates[template['templateName']]['templateId'],
                                    'templateType': template['templateType'],
                                    'subTemplates': subTemplates}
                            else:
                                template_item = {
                                    'templateId': feature_templates[template['templateName']]['templateId'],
                                    'templateType': template['templateType']}
                            generalTemplates.append(template_item)

                        payload['generalTemplates'] = generalTemplates
                        # payload['policyId'] = ''
                        if 'connectionPreference' in data:
                            payload['connectionPreference'] = data['connectionPreference']
                        if 'connectionPreferenceRequired' in data:
                            payload['connectionPreferenceRequired'] = data['connectionPreferenceRequired']
                        payload['featureTemplateUidRange'] = []
                        # payload['templateType'] = data['templateType']
                        # payload['templateMinVersion'] = data['templateMinVersion']
                        viptela.result['y_debug'] = data
                        viptela.result['z_debug'] = payload
                        viptela.request('/dataservice/template/device/feature', method='POST', data=json.dumps(payload))
                        viptela.result['changed'] = True

    # if the user is working with this module in only check mode we do not
    # want to make any changes to the environment, just return the current
    # state with no modifications
    # FIXME: Work with viptela so they can implement a check mode
    if module.check_mode:
        viptela.exit_json(**viptela.result)

    # execute checks for argument completeness

    # manipulate or modify the state as needed (this is going to be the
    # part where your module will do what it needs to do)

    # in the event of a successful module execution, you will want to
    # simple AnsibleModule.exit_json(), passing the key/value results
    viptela.exit_json(**viptela.result)

def main():
    run_module()

if __name__ == '__main__':
    main()