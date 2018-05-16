#!/usr/bin/python

# Copyright: (c) 2018, Aaron Smith <ajsmith10381@gmail.com>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type

ANSIBLE_METADATA = {'metadata_version': '1.1',
                    'status': ['preview'],
                    'supported_by': 'community'}


DOCUMENTATION = r'''
---
module: snowball_address
short_description: Manage addresses for AWS Snowball jobs.
description:
    - Create addresses for AWS Snowball jobs.
author: "Aaron Smith (@slapula)"
version_added: "2.6"
requirements: [ 'botocore', 'boto3' ]
options:
  name:
    description:
    - The name of a person to receive a Snowball at an address.
    required: true
  company:
    description:
    - The name of the company to receive a Snowball at an address.
  street1:
     description:
     - The first line in a street address that a Snowball is to be delivered to.
     required: true
  street2:
    description:
    - The second line in a street address that a Snowball is to be delivered to.
  street3:
    description:
    - The third line in a street address that a Snowball is to be delivered to.
  city:
    description:
    - The city in an address that a Snowball is to be delivered to.
    required: true
  state_or_province:
    description:
    - The state or province in an address that a Snowball is to be delivered to.
    required: true
  country:
     description:
     - The country in an address that a Snowball is to be delivered to.
     required: true
  postal_code:
    description:
    - The postal code in an address that a Snowball is to be delivered to.
    required: true
  phone_number:
    description:
    - The phone number associated with an address that a Snowball is to be delivered to.
    required: true
  restricted:
    description:
    - If the address you are creating is a primary address, then set this option to true.
    - This field is not supported in most regions.
    type: 'bool'
    default: false
extends_documentation_fragment:
    - ec2
    - aws
notes:
  - At this time, the AWS Snowball API does not support deleting or updating addresses.
  - These functions will be added when they become available.
'''


EXAMPLES = r'''
- name: add address for AWS Snowball usage
  snowball_address:
    name: 'Jed I. Knight'
    company: 'Galactic Security Incorporated'
    street1: '1337 Alder Run'
    street2: 'Suite 19'
    city: 'Orlando'
    state_or_province: 'Florida'
    country: 'USA'
    postal_code: '30400'
    phone_number: '555-555-5555'
'''


RETURN = r'''
address_id:
    description: The automatically generated ID for a specific address.
    returned: always
    type: string
'''

import os

from ansible.module_utils.aws.core import AnsibleAWSModule
from ansible.module_utils.ec2 import boto3_conn, get_aws_connection_info, AWSRetry
from ansible.module_utils.ec2 import camel_dict_to_snake_dict, boto3_tag_list_to_ansible_dict

try:
    from botocore.exceptions import BotoCoreError, ClientError
except ImportError:
    pass  # handled by AnsibleAWSModule


def address_exists(client, module, params, result):
    if module.check_mode:
        result['address_id'] = 'C3P01234ab12-3eec-4eb3-9be6-9374c10eb51b'
    try:
        response = client.describe_addresses()
        for i in response['Addresses']:
            current_id = i['AddressId']
            del i['AddressId']
            if i == params:
                result['address_id'] = current_id
                return True
    except (ClientError, IndexError):
        return False

    return False


def create_address(client, module, params, result):
    if module.check_mode:
        module.exit_json(changed=True, results=result)
    try:
        response = client.create_address(
            Address=params
        )
        result['address_id'] = response['AddressId']
        result['changed'] = True
        return result
    except (BotoCoreError, ClientError) as e:
        module.fail_json_aws(e, msg="Failed to create AWS Snowball address")


def main():
    module = AnsibleAWSModule(
        argument_spec={
            'name': dict(type='str', required=True),
            'company': dict(type='str'),
            'street1': dict(type='str', required=True),
            'street2': dict(type='str'),
            'street3': dict(type='str'),
            'city': dict(type='str', required=True),
            'state_or_province': dict(type='str', required=True),
            'country': dict(type='str', required=True),
            'postal_code': dict(type='str', required=True),
            'phone_number': dict(type='str', required=True),
            'restricted': dict(type='bool', default=False),
        },
        supports_check_mode=True,
    )

    result = {
        'changed': False
    }

    params = {}
    params['Name'] = module.params.get('name')
    if module.params.get('company'):
        params['Company'] = module.params.get('company')
    params['Street1'] = module.params.get('street1')
    if module.params.get('street2'):
        params['Street2'] = module.params.get('street2')
    if module.params.get('street3'):
        params['Street3'] = module.params.get('street3')
    params['City'] = module.params.get('city')
    params['StateOrProvince'] = module.params.get('state_or_province')
    params['Country'] = module.params.get('country')
    params['PostalCode'] = module.params.get('postal_code')
    params['PhoneNumber'] = module.params.get('phone_number')
    params['IsRestricted'] = module.params.get('restricted')

    client = module.client('snowball')

    address_status = address_exists(client, module, params, result)

    if not address_status:
        create_address(client, module, params, result)

    module.exit_json(changed=result['changed'], results=result)


if __name__ == '__main__':
    main()
