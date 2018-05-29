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
module: rekognition_stream_processor
short_description: Manage AWS Rekognition stream processors.
description:
    - Create, update, and delete stream processors on AWS Rekognition.
    - Stream processors consume live video from an AWS Kinesis Video Stream.
    - Face analysis of the streaming video is sent to an AWS Kinesis Data Stream.
author: "Aaron Smith (@slapula)"
version_added: "2.7"
requirements: [ 'botocore', 'boto3' ]
options:
  name:
    description:
    - An identifier you assign to the stream processor.
    required: true
  state:
    description:
    - Whether the stream processor should be exist or not.
    choices: ['present', 'absent']
    default: 'present'
  input_stream:
    description:
    - Kinesis video stream that provides the source streaming video.
    required: true
    suboptions:
      kinesis_video:
        description:
        - The Kinesis video input stream for the source streaming video.
        suboptions:
          arn:
            description:
            - ARN of the Amazon Kinesis Video Stream.
            required: true
  output_stream:
    description:
    - Kinesis data stream to which Rekognition Video puts the analysis results.
    required: true
    suboptions:
      kinesis_data:
        description:
        - The Amazon Kinesis Data Stream to which the Amazon Rekognition stream processor streams the analysis results.
        suboptions:
          arn:
            description:
            - ARN of the output Amazon Kinesis Data Stream.
  settings:
    description:
    - Face recognition input parameters to be used by the stream processor.
    required: true
    suboptions:
      face_search:
        description:
        - Face search settings to use on a streaming video.
        suboptions:
          collection_id:
            description:
            - The ID of a collection that contains faces that you want to search for.
          match_threshold:
            description:
            - Minimum face match confidence score that must be met to return a result for a recognized face.
  iam_role_arn:
    description:
    - ARN of the IAM role that allows access to the stream processor.
    required: true
extends_documentation_fragment:
    - ec2
    - aws
'''


EXAMPLES = r'''
- name: Create a stream processor
  rekognition_stream_processor:
    name: 'intersection27_stream'
    state: present
    input_stream:
      kinesis_video:
        arn: 'arn:aws:kinesisvideo:us-east-1:123456789012:stream/intersection27/0123456789012'
    output_stream:
      kinesis_data:
        arn: 'arn:aws:kinesis:us-east-1:123456789012:stream/intersection27'
    settings:
      face_search:
        collection_id: 'persons_of_interest'
        match_threshold: 90.0
    iam_role_arn: 'arn:aws:iam::123456789012:role/StreamProcessor'
'''


RETURN = r'''#'''

from ansible.module_utils.aws.core import AnsibleAWSModule
from ansible.module_utils.ec2 import boto3_conn, get_aws_connection_info, AWSRetry
from ansible.module_utils.ec2 import camel_dict_to_snake_dict, boto3_tag_list_to_ansible_dict

try:
    from botocore.exceptions import BotoCoreError, ClientError
except ImportError:
    pass  # handled by AnsibleAWSModule


def processor_exists(client, module, result):
    if module.check_mode:
        module.exit_json(changed=True)
    try:
        response = client.list_stream_processors()
        for i in response['StreamProcessors']:
            if i['Name'] == module.params.get('name'):
                stream_details = client.describe_stream_processor(
                    Name=module.params.get('name')
                )
                result['processor_config'] = stream_details
                return True
    except (BotoCoreError, ClientError) as e:
        module.fail_json_aws(e, msg="Failed to verify existence of stream processor")

    return False


def create_processor(client, module, params, result):
    if module.check_mode:
        module.exit_json(changed=True)
    try:
        response = client.create_stream_processor(**params)
        result['changed'] = True
        return result
    except (BotoCoreError, ClientError) as e:
        module.fail_json_aws(e, msg="Failed to create stream processor")

    return result


def update_processor(client, module, params, result):
    if module.check_mode:
        module.exit_json(changed=True)
    try:
        param_changed = []
        param_keys = list(params.keys())
        current_keys = list(result['processor_config'].keys())
        common_keys = set(param_keys) - (set(param_keys) - set(current_keys))
        for key in common_keys:
            if (params[key] != result['processor_config'][key]):
                param_changed.append(True)
            else:
                param_changed.append(False)
        if any(param_changed):
            if result['processor_config']['Status'] == 'STOPPED' or result['processor_config']['Status'] == 'FAILED':
                response = client.delete_stream_processor(
                    Name=module.params.get('name')
                )
                stream_delete_waiter(client, module)
                response = client.create_stream_processor(**params)
                result['changed'] = True
                return result
    except (BotoCoreError, ClientError) as e:
        module.fail_json_aws(e, msg="Failed to update stream processor")

    return result


def delete_processor(client, module, result):
    if module.check_mode:
        module.exit_json(changed=True)
    try:
        response = client.delete_stream_processor(
            Name=module.params.get('name')
        )
        result['changed'] = True
        return result
    except (BotoCoreError, ClientError) as e:
        module.fail_json_aws(e, msg="Failed to delete stream processor")

    return result


def main():
    module = AnsibleAWSModule(
        argument_spec={
            'name': dict(type='str', required=True),
            'state': dict(type='str', choices=['present', 'absent'], default='present'),
            'input_stream': dict(type='dict', required=True),
            'output_stream': dict(type='dict', required=True),
            'settings': dict(type='dict', required=True),
            'iam_role_arn': dict(type='str', required=True),
        },
        supports_check_mode=True,
    )

    result = {
        'changed': False,
        'status': ''
    }

    kinesis_input = {}
    kinesis_input['KinesisVideoStream'] = {}
    kinesis_input['KinesisVideoStream'].update({
        'Arn': module.params.get('input_stream').get('kinesis_video').get('arn')
    })

    kinesis_output = {}
    kinesis_output['KinesisDataStream'] = {}
    kinesis_output['KinesisDataStream'].update({
        'Arn': module.params.get('output_stream').get('kinesis_data').get('arn')
    })

    match_settings = {}
    match_settings['FaceSearch'] = {}
    match_settings['FaceSearch'].update({
        'CollectionId': module.params.get('settings').get('face_search').get('collection_id')
    })
    match_settings['FaceSearch'].update({
        'FaceMatchThreshold': module.params.get('settings').get('face_search').get('match_threshold')
    })


    params = {}
    params['Name'] = module.params.get('name')
    params['Input'] = {}
    params['Input'].update(kinesis_input)
    params['Output'] = {}
    params['Output'].update(kinesis_output)
    params['Settings'] = {}
    params['Settings'].update(match_settings)
    params['RoleArn'] = module.params.get('iam_role_arn')

    client = module.client('rekognition')

    processor_status = processor_exists(client, module, result)

    desired_state = module.params.get('state')

    if desired_state == 'present':
        if not processor_status:
            create_processor(client, module, params, result)
        if processor_status:
            update_processor(client, module, params, result)

    if desired_state == 'absent':
        if processor_status:
            delete_processor(client, module, result)

    module.exit_json(changed=result['changed'])


if __name__ == '__main__':
    main()
