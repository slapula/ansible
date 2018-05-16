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
module: snowball_job
short_description: Manage AWS Snowball jobs.
description:
    - Create, update, and cancel AWS Snowball jobs.
author: "Aaron Smith (@slapula)"
version_added: "2.6"
requirements: [ 'botocore', 'boto3' ]
options:
  state:
    description:
     - Whether the detector should be exist or not.
    required: true
    choices: ['present', 'absent']
  description:
    description:
    - Defines a description for this specific job.
    required: true
  job_type:
    description:
    -  Defines the type of job that you're creating.
    required: true
    choices: ['IMPORT', 'EXPORT', 'LOCAL_USE']
  resources:
    description:
    - Defines the Amazon S3 buckets associated with this job.
    required: true
    suboptions:
      s3_resources:
        description:
        - The resource types of only those AWS resources that you want to trigger an evaluation for the rule.
          You can only specify one type if you also specify a resource ID for `compliance_id`.
      lambda_resources:
        description:
        - The ID of the only AWS resource that you want to trigger an evaluation for the rule. If you specify a resource ID,
          you must specify one resource type for `compliance_types`.
  address_id:
    description:
    - The ID for the address that you want the Snowball shipped to.
    required: true
  kms_key_arn:
    description:
    - The KmsKeyARN that you want to associate with this job.
  role_arn:
    description:
    - The RoleARN that you want to associate with this job.
  capacity_preference:
    description:
    - Specify what size Snowball you'd like for this job.
    choices: ['T50', 'T80', 'T100', 'NoPreference']
    default: 'T80'
  shipping_option:
    description:
    - The shipping speed for this job.
    choices: ['SECOND_DAY', 'NEXT_DAY', 'EXPRESS', 'STANDARD']
    default: 'STANDARD'
  notification:
    description:
    - Defines the Amazon Simple Notification Service (Amazon SNS) notification settings for this job.
    suboptions:
      sns_topic_arn:
        description:
        - The new SNS TopicArn that you want to associate with this job.
      job_states_to_notify:
        description:
        - The list of job states that will trigger a notification for this job.
        type: 'list'
      notify_all:
        description:
        - Any change in job state will trigger a notification for this job.
        type: 'bool'
  cluster_id:
    description:
    - The ID of a cluster you'd like to add this job to.
    - If you're creating a job for a node in a cluster, you need to provide only this clusterId value.
    - The other job attributes are inherited from the cluster.
  snowball_type:
    description:
    - The type of AWS Snowball appliance to use for this job.
    - Only `EDGE` types are available for cluster jobs.
    choices: ['STANDARD', 'EDGE']
    default: 'STANDARD'
  forwarding_address_id:
    description:
    -  The forwarding address ID for a job.
extends_documentation_fragment:
    - ec2
    - aws
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
job_id:
    description: The automatically generated ID for the job.
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


def job_exists(client, module, result):
    if module.check_mode:
        result['job_id'] = 'JID123e4567-e89b-12d3-a456-426655440000'
    try:
        response = client.list_jobs()
        for i in response['JobListEntries']:
            if i['Description'] == module.params.get('description'):
                result['job_id'] = i['JobId']
                return True
    except (ClientError, IndexError):
        return False

    return False


def create_job(client, module, params, result):
    if module.check_mode:
        module.exit_json(changed=True, results=result)
    try:
        response = client.create_job(**params)
        result['job_id'] = response['JobId']
        result['changed'] = True
        return result
    except (BotoCoreError, ClientError) as e:
        module.fail_json_aws(e, msg="Failed to create AWS Snowball job")


def update_job(client, module, params, result):
    if module.check_mode:
        module.exit_json(changed=True, results=result)
    try:
        params['JobId'] = result['job_id']
        response = client.update_job(**params)
        result['changed'] = True
        return result
    except (BotoCoreError, ClientError) as e:
        module.fail_json_aws(e, msg="Failed to update AWS Snowball job")


def cancel_job(client, module, params, result):
    if module.check_mode:
        module.exit_json(changed=True, results=result)
    try:
        response = client.cancel_job(
            JobId=result['job_id']
        )
        result['changed'] = True
        return result
    except (BotoCoreError, ClientError) as e:
        module.fail_json_aws(e, msg="Failed to cancel AWS Snowball job")


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

    job_status = job_exists(client, module, result)

    desired_state = module.params.get('state')

    if desired_state == 'present':
        if not job_status:
            create_job(client, module, params, result)
        if job_status:
            update_job(client, module, params, result)

    if desired_state == 'absent':
        if job_status:
            delete_job(client, module, result)

    module.exit_json(changed=result['changed'], results=result)


if __name__ == '__main__':
    main()
