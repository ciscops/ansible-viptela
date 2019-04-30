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
import os.path
# from requests.auth import HTTPBasicAuth
# from paramiko import SSHClient
# from scp import SCPClient
from ansible.module_utils.basic import AnsibleModule, json
from ansible.module_utils.viptela import viptelaModule, viptela_argument_spec


def run_module():
    # define available arguments/parameters a user can pass to the module
    argument_spec = viptela_argument_spec()
    argument_spec.update(file=dict(type='str', required=True),
                         )

    # seed the result dict in the object
    # we primarily care about changed and state
    # change is if this module effectively modified the target
    # state will include any data that you want your module to pass back
    # for consumption, for example, in a subsequent task
    result = dict(
        changed=False,
        original_message='',
        message=''
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

    # manipulate or modify the state as needed (this is going to be the
    # part where your module will do what it needs to do)
    # result['original_message'] = module.params['name']

    # use whatever logic you need to determine whether or not this module
    # made any modifications to your target
    # if module.params['new']:
    #     result['changed'] = True

    response = viptela.request('/dataservice/system/device/fileupload', method='POST',
                               files={'file': open(module.params['file'])},
                               data={'validity':'valid', 'upload':'true'},
                               headers=None)

    json = response.json()
    viptela.result['json'] = json
    viptela.result['msg'] = json['vedgeListUploadStatus']
    if 'successfully' in json['vedgeListUploadStatus']:
        viptela.result['changed'] = True

    # if the user is working with this module in only check mode we do not
    # want to make any changes to the environment, just return the current
    # state with no modifications
    # FIXME: Work with viptela so they can implement a check mode
    if module.check_mode:
        viptela.exit_json()

    # execute checks for argument completeness

    # manipulate or modify the state as needed (this is going to be the
    # part where your module will do what it needs to do)

    # in the event of a successful module execution, you will want to
    # simple AnsibleModule.exit_json(), passing the key/value results
    viptela.exit_json()

def main():
    run_module()

if __name__ == '__main__':
    main()