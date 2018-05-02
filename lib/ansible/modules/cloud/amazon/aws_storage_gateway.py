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
module: aws_storage_gateway
short_description: Manage AWS Storage Gateway resources
description:
    - Module manages AWS Config resources
    - Supported resource types include gateway.
version_added: "2.6"
requirements: [ 'botocore', 'boto3' ]
author:
    - "Aaron Smith (@slapula)"
options:
  state:
    description:
    - Whether the resource should be present or absent.
    default: present
    choices: ['present', 'absent']
  resource_type:
    description:
    - The type of AWS Storage Gateway resource you are manipulating.
    required: true
    choices: ['gateway', 'nfs_file_share', 'cached_iscsi_volume', 'stored_iscsi_volume', 'tape', 'tape_group']
  activation_key:
    description:
    - Your gateway activation key. See AWS documentation on how to acquire this key.
    - Resource type `gateway`
  name:
    description:
    - The name you configured for your gateway.
    - Resource type `gateway`
  timezone:
    description:
    - A value that indicates the time zone you want to set for the gateway.
    - Resource type `gateway`
  gateway_region:
    description:
    - A value that indicates the region where you want to store your data.
    - Resource type `gateway`
  gateway_type:
    description:
    - A value that defines the type of gateway to activate.
    - The type specified is critical to all later functions of the gateway and cannot be changed after activation.
    - Resource type `gateway`
    default: 'STORED'
    choices: ['STORED', 'CACHED', 'VTL', 'FILE_S3']
  tape_drive_type:
    description:
    - The value that indicates the type of tape drive to use for tape gateway.
    - Resource type `gateway`
    choices: ['IBM-ULT3580-TD5']
  medium_changer_type:
    description:
    - The value that indicates the type of medium changer to use for tape gateway.
    - Resource type `gateway`
    choices: ['STK-L700', 'AWS-Gateway-VTL']
  nfs_token:
    description:
    - A unique string value that you supply that is used by file gateway to ensure idempotent file share creation.
    - Resource type `nfs_file_share`
  nfs_defaults:
    description:
    - File share default values.
    - Resource type `nfs_file_share`
    suboptions:
      file_mode:
        description:
        - The Unix file mode in the form "nnnn".
      directory_mode:
        description:
        - The Unix directory mode in the form "nnnn".
      group_id:
        description:
        - The default group ID for the file share.
      owner_id:
        description:
        - The default owner ID for files in the file share.
  gateway_arn:
    description:
    - The Amazon Resource Name (ARN) of the file gateway on which you want to create a file share.
    - Resource type `nfs_file_share`
  kms_encrypted:
    description:
    - True to use Amazon S3 server side encryption with your own AWS KMS key, or false to use a key managed by Amazon S3.
    - Resource type `nfs_file_share`
    type: bool
  kms_key:
    description:
    - The KMS key used for Amazon S3 server side encryption.
    - Resource type `nfs_file_share`
  iam_role:
    description:
    - The ARN of the AWS Identity and Access Management (IAM) role that a file gateway assumes when it accesses the underlying storage.
    - Resource type `nfs_file_share`
  location_arn:
    description:
    - The ARN of the backed storage used for storing file data.
    - Resource type `nfs_file_share`
  default_storage_class:
    description:
    - The default storage class for objects put into an Amazon S3 bucket by file gateway.
    - Resource type `nfs_file_share`
    default: 'S3_STANDARD'
    choices: ['S3_STANDARD', 'S3_STANDARD_IA']
  object_acl:
    description:
    - Sets the access control list permission for objects in the Amazon S3 bucket that a file gateway puts objects into.
    - Resource type `nfs_file_share`
    default: 'private'
  client_list:
    description:
    - The list of clients that are allowed to access the file gateway. The list must contain either valid IP addresses or valid CIDR blocks.
    - Resource type `nfs_file_share`
  squash:
    description:
    - Maps a user to anonymous user.
    - Resource type `nfs_file_share`
    choices: ['RootSquash', 'NoSquash', 'AllSquash']
  read_only:
    description:
    - Sets the write status of a file share.
    - Resource type `nfs_file_share`
    type: bool
  guess_mime_type_enabled:
    description:
    - Enables guessing of the MIME type for uploaded objects based on file extensions.
    - Resource type `nfs_file_share`
    type: bool
    default: 'true'
  requester_pays:
    description:
    - Sets who pays the cost of the request and the data download from the Amazon S3 bucket.
    - Resource type `nfs_file_share`
    type: bool
    default: 'false'
  volume_size:
    description:
    - The size, in bytes, of the cached volume that you want to create.
    - Resource type `cached_iscsi_volume`
  snapshot_id:
    description:
    - The snapshot ID (e.g. "snap-1122aabb") of the snapshot to restore as the new stored volume.
    - Specify this field if you want to create the iSCSI storage volume from a snapshot otherwise do not include this field.
    - Resource type `cached_iscsi_volume`
  target_name:
    description:
    - Name of the ISCSI Target.
    - Resource type `cached_iscsi_volume` or `stored_iscsi_volume`
  source_volume_arn:
    description:
    - The ARN for an existing volume.
    - Specifying this ARN makes the new volume into an exact copy of the specified existing volume's latest recovery point.
    - The `volume_size` value for this new volume must be equal to or larger than the size of the existing volume, in bytes.
    - Resource type `cached_iscsi_volume`
  network_interface:
    description:
    - The network interface of the gateway on which to expose the iSCSI target.
    - Only IPv4 addresses are accepted.
    - Resource type `cached_iscsi_volume` or `stored_iscsi_volume`
  volume_token:
    description:
    - A unique identifier that you use to retry a request.
    - Using the same `volume_token` prevents creating the volume multiple times.
    - Resource type `cached_iscsi_volume`
  disk_id:
    description:
    - The unique identifier for the gateway local disk that is configured as a stored volume.
    - Resource type `stored_iscsi_volume`
  preserve_existing_data:
    description:
    - Specify this field as true if you want to preserve the data on the local disk. Otherwise, specifying this field as false creates an empty volume.
    - Resource type `stored_iscsi_volume`
    type: bool
  tape_barcode:
    description:
    - The barcode of the virtual tape you are creating.
    - Resource type `tape`
  tape_size:
    description:
    - The size, in bytes, of the virtual tapes that you want to create.
    - The size must be aligned by gigabyte (1024*1024*1024 byte).
    - Resource type `tape_group`
  tape_token:
    description:
    - A unique identifier that you use to retry a request.
    - Using the same `tape_token` prevents creating the tape multiple times.
    - Resource type `tape_group`
  number_of_tapes:
    description:
    - The number of virtual tapes that you want to create.
    - Resource type `tape_group`
  tape_barcode_prefix:
    description:
    - A prefix that you append to the barcode of the virtual tape you are creating.
    - Resource type `tape_group`
extends_documentation_fragment:
  - aws
  - ec2
'''

EXAMPLES = r'''
this is a test
'''

RETURN = r'''#'''

import time

try:
    import botocore
    from botocore.exceptions import BotoCoreError, ClientError
except ImportError:
    pass  # handled by AnsibleAWSModule

from ansible.module_utils.aws.core import AnsibleAWSModule
from ansible.module_utils.ec2 import boto3_conn, get_aws_connection_info, AWSRetry
from ansible.module_utils.ec2 import camel_dict_to_snake_dict, boto3_tag_list_to_ansible_dict


def resource_exists(client, tagger, module, resource_type, params, result):
    if resource_type == 'gateway':
        try:
            gateway_list = client.list_gateways()
            for i in gateway_list['Gateways']:
                if i['GatewayName'] == params['GatewayName']:
                    result['GatewayARN'] = i['GatewayARN']
                    return True
        except (botocore.exceptions.ClientError, botocore.exceptions.BotoCoreError):
            return False

    if resource_type == 'nfs_file_share':
        try:
            file_share_list = client.list_file_shares()
            for i in file_share_list['FileShareInfoList']:
                file_share_deets = client.describe_nfs_file_shares(
                    FileShareARNList=[i['FileShareARN']]
                )
                if file_share_deets['NFSFileShareInfoList'][0]['LocationARN'] == params['LocationARN']:
                    result['FileShareARN'] = i['FileShareARN']
                    return True
        except (botocore.exceptions.ClientError, botocore.exceptions.BotoCoreError):
            return False

    if resource_type == 'cached_iscsi_volume' or resource_type == 'stored_iscsi_volume':
        try:
            resource_exists = tagger.get_resources(
                TagFilters=[
                    {
                        'Key': 'TargetName',
                        'Values': [params['TargetName']]
                    },
                    {
                        'Key': 'GatewayARN',
                        'Values': [params['GatewayARN']]
                    },
                ]
            )
            if resource_exists['ResourceTagMappingList']:
                result['VolumeARN'] = resource_exists['ResourceTagMappingList'][0]['ResourceARN']
                return True
        except (botocore.exceptions.ClientError, botocore.exceptions.BotoCoreError):
            return False

    if resource_type == 'tape':
        try:
            tape_list = client.list_tapes()
            for i in tape_list['TapeInfos']:
                if i['TapeBarcode'] == params['TapeBarcode']:
                    result['TapeARN'] = i['TapeARN']
                    return True
        except (botocore.exceptions.ClientError, botocore.exceptions.BotoCoreError):
            return False

    return False


def create_resource(client, tagger, module, resource_type, params, result):
    if resource_type == 'gateway':
        try:
            gw_response = client.activate_gateway(**params)
            time.sleep(10)  # Need a waiter here but it doesn't exist yet in the StorageGateway API
            disks_response = client.list_local_disks(
                GatewayARN=gw_response['GatewayARN']
            )
            if disks_response['Disks']:
                if params['GatewayType'] == 'FILE_S3':
                    vol_response = client.add_cache(
                        GatewayARN=gw_response['GatewayARN'],
                        DiskIds=[disks_response['Disks'][0]['DiskId']]
                    )
                if params['GatewayType'] == 'CACHED' or params['GatewayType'] == 'VTL':
                    vol_response = client.add_cache(
                        GatewayARN=gw_response['GatewayARN'],
                        DiskIds=[disks_response['Disks'][0]['DiskId']]
                    )
                    vol_response = client.add_upload_buffer(
                        GatewayARN=gw_response['GatewayARN'],
                        DiskIds=[disks_response['Disks'][1]['DiskId']]
                    )
                if params['GatewayType'] == 'STORED':
                    vol_response = client.add_upload_buffer(
                        GatewayARN=gw_response['GatewayARN'],
                        DiskIds=[disks_response['Disks'][0]['DiskId']]
                    )
                    vol_response = client.add_working_storage(
                        GatewayARN=gw_response['GatewayARN'],
                        DiskIds=[disks_response['Disks'][1]['DiskId']]
                    )
            result['GatewayARN'] = gw_response['GatewayARN']
            result['changed'] = True
            return result
        except (botocore.exceptions.ClientError, botocore.exceptions.BotoCoreError) as e:
            module.fail_json_aws(e, msg="Couldn't activate storage gateway instance")

    if resource_type == 'nfs_file_share':
        try:
            fs_response = client.create_nfs_file_share(**params)
            result['FileShareARN'] = fs_response['FileShareARN']
            result['changed'] = True
            return result
        except (botocore.exceptions.ClientError, botocore.exceptions.BotoCoreError) as e:
            module.fail_json_aws(e, msg="Couldn't create NFS file share")

    if resource_type == 'cached_iscsi_volume':
        try:
            vol_response = client.create_cached_iscsi_volume(**params)
            tag_response = tagger.tag_resources(
                ResourceARNList=[
                    vol_response['VolumeARN'],
                ],
                Tags={
                    'GatewayARN': params['GatewayARN'],
                    'TargetName': params['TargetName'],
                    'VolumeARN': vol_response['VolumeARN']
                }
            )
            result['VolumeARN'] = vol_response['VolumeARN']
            result['changed'] = True
            return result
        except (botocore.exceptions.ClientError, botocore.exceptions.BotoCoreError) as e:
            module.fail_json_aws(e, msg="Couldn't create cached ISCSI volume")

    if resource_type == 'stored_iscsi_volume':
        try:
            vol_response = client.create_stored_iscsi_volume(**params)
            tag_response = tagger.tag_resources(
                ResourceARNList=[
                    vol_response['VolumeARN'],
                ],
                Tags={
                    'GatewayARN': params['GatewayARN'],
                    'TargetName': params['TargetName'],
                    'VolumeARN': vol_response['VolumeARN']
                }
            )
            result['VolumeARN'] = vol_response['VolumeARN']
            result['changed'] = True
            return result
        except (botocore.exceptions.ClientError, botocore.exceptions.BotoCoreError) as e:
            module.fail_json_aws(e, msg="Couldn't create stored ISCSI volume")

    if resource_type == 'tape':
        try:
            tp_response = client.create_tape_with_barcode(**params)
            result['TapeARN'] = tp_response['TapeARN']
            result['changed'] = True
            return result
        except (botocore.exceptions.ClientError, botocore.exceptions.BotoCoreError) as e:
            module.fail_json_aws(e, msg="Couldn't create tape")

    if resource_type == 'tape_group':
        try:
            tp_response = client.create_tapes(**params)
            result['TapeARNs'] = tp_response['TapeARNs']
            result['changed'] = True
            return result
        except (botocore.exceptions.ClientError, botocore.exceptions.BotoCoreError) as e:
            module.fail_json_aws(e, msg="Couldn't create tapes")

    return result


def update_resource(client, module, resource_type, params, result):
    if resource_type == 'gateway':
        current_params = client.describe_gateway_information(
            GatewayARN=result['GatewayARN']
        )

        if params['GatewayName'] != current_params['GatewayName'] or params['GatewayTimezone'] != current_params['GatewayTimezone']:
            try:
                response = client.update_gateway_information(
                    GatewayARN=result['GatewayARN'],
                    GatewayName=params['GatewayName'],
                    GatewayTimezone=params['GatewayTimezone']
                )
                result['GatewayARN'] = response['GatewayARN']
                result['changed'] = True
                return result
            except (botocore.exceptions.ClientError, botocore.exceptions.BotoCoreError) as e:
                module.fail_json_aws(e, msg="Couldn't update storage gateway")

    if resource_type == 'nfs_file_share':
        current_params = client.describe_nfs_file_shares(
            FileShareARNList=[result['FileShareARN']]
        )

        updated_params = {}
        param_changed = []
        updated_params['FileShareARN'] = result['FileShareARN']
        if module.params.get('nfs_defaults'):
            if params['NFSFileShareDefaults'] != current_params['NFSFileShareInfoList'][0]['NFSFileShareDefaults']
                updated_params['NFSFileShareDefaults'] = params['NFSFileShareDefaults']
                param_changed.append(True)
            else:
                param_changed.append(False)
        if module.params.get('kms_encrypted'):
            if params['KMSEncrypted'] != current_params['NFSFileShareInfoList'][0]['KMSEncrypted']:
                updated_params['KMSEncrypted'] = params['KMSEncrypted']
                param_changed.append(True)
            else:
                param_changed.append(False)
        if module.params.get('kms_key'):
            if params['KMSKey'] != current_params['NFSFileShareInfoList'][0]['KMSKey']:
                updated_params['KMSKey'] = params['KMSKey']
                param_changed.append(True)
            else:
                param_changed.append(False)
        if module.params.get('default_storage_class'):
            if params['DefaultStorageClass'] != current_params['NFSFileShareInfoList'][0]['DefaultStorageClass']:
                updated_params['DefaultStorageClass'] = params['DefaultStorageClass']
                param_changed.append(True)
            else:
                param_changed.append(False)
        if module.params.get('object_acl'):
            if params['ObjectACL'] != current_params['NFSFileShareInfoList'][0]['ObjectACL']:
                updated_params['ObjectACL'] = params['ObjectACL']
                param_changed.append(True)
            else:
                param_changed.append(False)
        if module.params.get('client_list'):
            if params['ClientList'] != current_params['NFSFileShareInfoList'][0]['ClientList']:
                updated_params['ClientList'] = params['ClientList']
                param_changed.append(True)
            else:
                param_changed.append(False)
        if module.params.get('squash'):
            if params['Squash'] != current_params['NFSFileShareInfoList'][0]['Squash']:
                updated_params['Squash'] = params['Squash']
                param_changed.append(True)
            else:
                param_changed.append(False)
        if module.params.get('read_only'):
            if params['ReadOnly'] != current_params['NFSFileShareInfoList'][0]['ReadOnly']:
                updated_params['ReadOnly'] = params['ReadOnly']
                param_changed.append(True)
            else:
                param_changed.append(False)
        if module.params.get('guess_mime_type_enabled'):
            if params['GuessMIMETypeEnabled'] != current_params['NFSFileShareInfoList'][0]['GuessMIMETypeEnabled']:
                updated_params['GuessMIMETypeEnabled'] = params['GuessMIMETypeEnabled']
                param_changed.append(True)
            else:
                param_changed.append(False)
        if module.params.get('requester_pays'):
            if params['RequesterPays'] != current_params['NFSFileShareInfoList'][0]['RequesterPays']:
                updated_params['RequesterPays'] = params['RequesterPays']
                param_changed.append(True)
            else:
                param_changed.append(False)

        if any(param_changed):
            try:
                response = client.update_nfs_file_share(**updated_params)
                result['FileShareARN'] = response['FileShareARN']
                result['changed'] = True
                return result
            except (botocore.exceptions.ClientError, botocore.exceptions.BotoCoreError) as e:
                module.fail_json_aws(e, msg="Couldn't update storage gateway")

    return result


def delete_resource(client, module, resource_type, params, result):
    if resource_type == 'gateway':
        try:
            response = client.delete_gateway(
                GatewayARN=result['GatewayARN']
            )
            result['changed'] = True
            return result
        except (botocore.exceptions.ClientError, botocore.exceptions.BotoCoreError) as e:
            module.fail_json_aws(e, msg="Couldn't delete storage gateway")

    if resource_type == 'nfs_file_share':
        try:
            response = client.delete_file_share(
                FileShareARN=result['FileShareARN']
            )
            result['changed'] = True
            return result
        except (botocore.exceptions.ClientError, botocore.exceptions.BotoCoreError) as e:
            module.fail_json_aws(e, msg="Couldn't delete NFS file share")

    if resource_type == 'cached_iscsi_volume' or resource_type == 'stored_iscsi_volume':
        try:
            response = client.delete_volume(
                VolumeARN=result['VolumeARN']
            )
            result['changed'] = True
            return result
        except (botocore.exceptions.ClientError, botocore.exceptions.BotoCoreError) as e:
            module.fail_json_aws(e, msg="Couldn't delete cached or stored volume")

    if resource_type == 'tape':
        try:
            response = client.delete_tape(
                GatewayARN=params['GatewayARN'],
                TapeARN=result['TapeARN']
            )
            result['changed'] = True
            return result
        except (botocore.exceptions.ClientError, botocore.exceptions.BotoCoreError) as e:
            module.fail_json_aws(e, msg="Couldn't delete tape")

    return result


def main():
    requirements = [
        ('resource_type', 'gateway', ['activation_key', 'name', 'timezone', 'gateway_region']),
        ('resource_type', 'nfs_file_share', ['nfs_token', 'gateway_arn', 'iam_role', 'location_arn']),
        ('resource_type', 'cached_iscsi_volume', ['gateway_arn', 'volume_size', 'target_name', 'network_interface', 'volume_token']),
        ('resource_type', 'stored_iscsi_volume', ['gateway_arn', 'disk_id', 'preserve_existing_data', 'target_name', 'network_interface']),
        ('resource_type', 'tape', ['gateway_arn', 'tape_size', 'tape_barcode']),
        ('resource_type', 'tape_group', ['gateway_arn', 'tape_size', 'tape_token', 'number_of_tapes', 'tape_barcode_prefix'])
    ]

    module = AnsibleAWSModule(
        argument_spec={
            'state': dict(type='str', choices=['present', 'absent'], default='present'),
            'resource_type': dict(
                type='str',
                choices=[
                    'gateway',
                    'nfs_file_share',
                    'cached_iscsi_volume',
                    'stored_iscsi_volume',
                    'tape',
                    'tape_group'
                ],
                required=True
            ),
            'activation_key': dict(type='str'),
            'name': dict(type='str'),
            'timezone': dict(type='str'),
            'gateway_region': dict(type='str'),
            'gateway_type': dict(type='str', default='STORED', choices=['STORED', 'CACHED', 'VTL', 'FILE_S3']),
            'tape_drive_type': dict(type='str', choices=['IBM-ULT3580-TD5']),
            'medium_changer_type': dict(type='str', choices=['STK-L700', 'AWS-Gateway-VTL']),
            'nfs_token': dict(type='str'),
            'nfs_defaults': dict(type='dict'),
            'gateway_arn': dict(type='str'),
            'kms_encrypted': dict(type='bool', default=False),
            'kms_key': dict(type='str'),
            'iam_role': dict(type='str'),
            'location_arn': dict(type='str'),
            'default_storage_class': dict(type='str', default='S3_STANDARD', choices=['S3_STANDARD', 'S3_STANDARD_IA']),
            'object_acl': dict(type='str', default='private'),
            'client_list': dict(type='list'),
            'squash': dict(type='str', choices=['RootSquash', 'NoSquash', 'AllSquash']),
            'read_only': dict(type='bool', default=False),
            'guess_mime_type_enabled': dict(type='bool', default=True),
            'requester_pays': dict(type='bool', default=False),
            'volume_size': dict(type='int'),
            'snapshot_id': dict(type='str'),
            'target_name': dict(type='str'),
            'source_volume_arn': dict(type='str'),
            'network_interface': dict(type='str'),
            'volume_token': dict(type='str'),
            'disk_id': dict(type='str'),
            'preserve_existing_data': dict(type='bool'),
            'tape_barcode': dict(type='str'),
            'tape_size': dict(type='int'),
            'tape_token': dict(type='str'),
            'number_of_tapes': dict(type='int'),
            'tape_barcode_prefix': dict(type='str')
        },
        supports_check_mode=False,
        required_if=requirements,
    )

    result = {
        'changed': False
    }

    state = module.params.get('state')
    resource_type = module.params.get('resource_type')

    if resource_type == 'gateway':
        params = {}
        if module.params.get('activation_key'):
            params['ActivationKey'] = module.params.get('activation_key')
        if module.params.get('name'):
            params['GatewayName'] = module.params.get('name')
        if module.params.get('timezone'):
            params['GatewayTimezone'] = module.params.get('timezone')
        if module.params.get('gateway_region'):
            params['GatewayRegion'] = module.params.get('gateway_region')
        if module.params.get('gateway_type'):
            params['GatewayType'] = module.params.get('gateway_type')
        if module.params.get('tape_drive_type'):
            params['TapeDriveType'] = module.params.get('tape_drive_type')
        if module.params.get('medium_changer_type'):
            params['MediumChangerType'] = module.params.get('medium_changer_type')

    if resource_type == 'nfs_file_share':
        params = {}
        if module.params.get('nfs_token'):
            params['ClientToken'] = module.params.get('nfs_token')
        if module.params.get('nfs_defaults'):
            params['NFSFileShareDefaults'] = {}
            if module.params.get('nfs_defaults').get('file_mode'):
                params['NFSFileShareDefaults'].update({
                    'FileMode': module.params.get('nfs_defaults').get('file_mode')
                })
            if module.params.get('nfs_defaults').get('directory_mode'):
                params['NFSFileShareDefaults'].update({
                    'DirectoryMode': module.params.get('nfs_defaults').get('directory_mode')
                })
            if module.params.get('nfs_defaults').get('group_id'):
                params['NFSFileShareDefaults'].update({
                    'GroupId': module.params.get('nfs_defaults').get('group_id')
                })
            if module.params.get('nfs_defaults').get('owner_id'):
                params['NFSFileShareDefaults'].update({
                    'OwnerId': module.params.get('nfs_defaults').get('owner_id')
                })
        if module.params.get('gateway_arn'):
            params['GatewayARN'] = module.params.get('gateway_arn')
        if module.params.get('kms_encrypted'):
            params['KMSEncrypted'] = module.params.get('kms_encrypted')
        if module.params.get('kms_key'):
            params['KMSKey'] = module.params.get('kms_key')
        if module.params.get('iam_role'):
            params['Role'] = module.params.get('iam_role')
        if module.params.get('location_arn'):
            params['LocationARN'] = module.params.get('location_arn')
        if module.params.get('default_storage_class'):
            params['DefaultStorageClass'] = module.params.get('default_storage_class')
        if module.params.get('object_acl'):
            params['ObjectACL'] = module.params.get('object_acl')
        if module.params.get('client_list'):
            params['ClientList'] = module.params.get('client_list')
        if module.params.get('squash'):
            params['Squash'] = module.params.get('squash')
        if module.params.get('read_only'):
            params['ReadOnly'] = module.params.get('read_only')
        if module.params.get('guess_mime_type_enabled'):
            params['GuessMIMETypeEnabled'] = module.params.get('guess_mime_type_enabled')
        if module.params.get('requester_pays'):
            params['RequesterPays'] = module.params.get('requester_pays')

    if resource_type == 'cached_iscsi_volume':
        params = {}
        if module.params.get('gateway_arn'):
            params['GatewayARN'] = module.params.get('gateway_arn')
        if module.params.get('volume_size'):
            params['VolumeSizeInBytes'] = module.params.get('volume_size')
        if module.params.get('snapshot_id'):
            params['SnapshotId'] = module.params.get('snapshot_id')
        if module.params.get('target_name'):
            params['TargetName'] = module.params.get('target_name')
        if module.params.get('source_volume_arn'):
            params['SourceVolumeARN'] = module.params.get('source_volume_arn')
        if module.params.get('network_interface'):
            params['NetworkInterfaceId'] = module.params.get('network_interface')
        if module.params.get('volume_token'):
            params['ClientToken'] = module.params.get('volume_token')

    if resource_type == 'stored_iscsi_volume':
        params = {}
        if module.params.get('gateway_arn'):
            params['GatewayARN'] = module.params.get('gateway_arn')
        if module.params.get('disk_id'):
            params['DiskId'] = module.params.get('disk_id')
        if module.params.get('snapshot_id'):
            params['SnapshotId'] = module.params.get('snapshot_id')
        if module.params.get('preserve_existing_data'):
            params['PreserveExistingData'] = module.params.get('preserve_existing_data')
        if module.params.get('target_name'):
            params['TargetName'] = module.params.get('target_name')
        if module.params.get('network_interface'):
            params['NetworkInterfaceId'] = module.params.get('network_interface')

    if resource_type == 'tape':
        params = {}
        if module.params.get('gateway_arn'):
            params['GatewayARN'] = module.params.get('gateway_arn')
        if module.params.get('tape_size'):
            params['TapeSizeInBytes'] = module.params.get('tape_size')
        if module.params.get('tape_barcode'):
            params['TapeBarcode'] = module.params.get('tape_barcode')

    if resource_type == 'tape_group':
        params = {}
        if module.params.get('gateway_arn'):
            params['GatewayARN'] = module.params.get('gateway_arn')
        if module.params.get('tape_size'):
            params['TapeSizeInBytes'] = module.params.get('tape_size')
        if module.params.get('tape_token'):
            params['ClientToken'] = module.params.get('tape_token')
        if module.params.get('number_of_tapes'):
            params['NumTapesToCreate'] = module.params.get('number_of_tapes')
        if module.params.get('tape_barcode_prefix'):
            params['TapeBarcodePrefix'] = module.params.get('tape_barcode_prefix')

    region, ec2_url, aws_connect_kwargs = get_aws_connection_info(module, boto3=True)
    client = boto3_conn(module, conn_type='client', resource='storagegateway', region=region, endpoint=ec2_url, **aws_connect_kwargs)
    tagger = boto3_conn(module, conn_type='client', resource='resourcegroupstaggingapi', region=region, endpoint=ec2_url, **aws_connect_kwargs)

    resource_status = resource_exists(client, tagger, module, resource_type, params, result)

    if state == 'present':
        if not resource_status:
            create_resource(client, tagger, module, resource_type, params, result)
        if resource_status:
            update_resource(client, module, resource_type, params, result)

    if state == 'absent':
        if resource_status:
            delete_resource(client, module, resource_type, params, result)

    module.exit_json(changed=result['changed'], results=result)


if __name__ == '__main__':
    main()
