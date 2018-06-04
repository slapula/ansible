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
module: aws_neptune_instance
short_description: Manage graph database instances on AWS Neptune.
description:
    - Create, modify, and destroy graph database instances on AWS Neptune
version_added: "2.7"
requirements: [ 'botocore>=1.10.0', 'boto3' ]
author:
    - "Aaron Smith (@slapula)"
options:
  name:
    description:
    - The DB instance identifier.
    required: true
  state:
    description:
    - Whether the resource should be present or absent.
    default: present
    choices: ['present', 'absent']
  database_name:
    description:
    - The database name.
  instance_class:
    description:
    - The compute and memory capacity of the DB instance, for example, `db.m4.large`.
    - Not all DB instance classes are available in all AWS Regions.
  db_engine:
    description:
    - The name of the database engine to be used for this DB instance.
    choices: ['neptune']
    default: 'neptune'
  master_username:
    description:
    - The name for the master user.
  master_password:
    description:
    - The password for the master user.
  db_security_groups:
    description:
    - A list of DB security groups to associate with this DB instance.
  vpc_security_groups:
    description:
    - A list of EC2 VPC security groups to associate with this DB instance.
  availability_zone:
    description:
    - The EC2 Availability Zone that the DB instance is created in.
  db_subnet_group:
    description:
    - A DB subnet group to associate with this DB instance.
  maintenance_window:
    description:
    - The weekly time range during which system maintenance can occur, in Universal Coordinated Time (UTC).
  parameter_group:
    description:
    - The name of the DB parameter group to associate with this DB instance.
    - If this argument is omitted, the default is used.
  multi_az:
    description:
    - Specifies if the DB instance is a Multi-AZ deployment.
    - You can't set the `availability_zone` parameter if the `multi_az` parameter is set to true.
    type: bool
    default: false
  db_engine_version:
    description:
    - The version number of the database engine to use.
  auto_minor_version_upgrade:
    description:
    - Indicates that minor engine upgrades are applied automatically to the DB instance during the maintenance window.
    type: bool
    default: true
  license_model:
    description:
    - License model information for this DB instance.
    choices: ['license-included', 'bring-your-own-license', 'general-public-license']
  iops:
    description:
    - The amount of Provisioned IOPS (input/output operations per second) to be initially allocated for the DB instance.
  option_group:
    description:
    - Indicates that the DB instance should be associated with the specified option group.
  publicly_accessible:
    description:
    - Specifies the accessibility options for the DB instance.
    type: bool
  db_cluster:
    description:
    - The identifier of the DB cluster that the instance will belong to.
  tde_credential_arn:
    description:
    - The ARN from the key store with which to associate the instance for TDE encryption.
  tde_credential_password:
    description:
    - The password for the given ARN from the key store in order to access the device.
  domain:
    description:
    - Specify the Active Directory Domain to create the instance in.
  copy_tags_to_snapshot:
     description:
     - True to copy all tags from the DB instance to snapshots of the DB instance, and otherwise false.
     type: bool
     default: false
  monitoring_interval:
    description:
    - The interval, in seconds, between points when Enhanced Monitoring metrics are collected for the DB instance.
    - To disable collecting Enhanced Monitoring metrics, specify 0. The default is 0.
    - If `monitoring_role_arn` is specified, then you must also set `monitoring_interval` to a value other than 0.
    choices: [0, 1, 5, 10, 15, 30, 60]
    default: 0
  monitoring_role_arn:
    description:
    - The ARN for the IAM role that permits Neptune to send enhanced monitoring metrics to Amazon CloudWatch Logs.
    - If `monitoring_interval` is set to a value other than 0, then you must supply a `monitoring_role_arn` value.
  domain_role_arn:
    description:
    - Specify the name of the IAM role to be used when making API calls to the Directory Service.
  promotion_tier:
    description:
    - A value that specifies the order in which an Read Replica is promoted to the primary instance after a failure of the existing primary instance.
    choices: [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15]
  timezone:
    description:
    - The time zone of the DB instance.
  enable_iam_auth:
    description:
    - True to enable mapping of AWS Identity and Access Management (IAM) accounts to database accounts, and otherwise false.
    type: bool
    default: false
  enable_performance_insights:
    description:
    - True to enable Performance Insights for the DB instance, and otherwise false.
    type: bool
    default: false
  performance_insights_kms_key:
    description:
    - The AWS KMS key identifier for encryption of Performance Insights data.
  enable_cloudwatch_logs_export:
    description:
    - The list of log types that need to be enabled for exporting to CloudWatch Logs.
  skip_final_snapshot:
    description:
    - Determines whether a final DB instance snapshot is created before the DB instance is deleted.
    type: bool
    default: false
  final_snapshot_id:
    description:
    - The DB instance snapshot identifier of the new DB instance snapshot created when `skip_final_snapshot` is set to false .
extends_documentation_fragment:
  - aws
  - ec2
'''

EXAMPLES = r'''
  - name: Create a new graph database instance
    aws_neptune_instance:
      name: "example-cluster-instance"
      state: present
      instance_class: 'db.m4.xlarge'
      db_cluster: 'example-cluster'
      skip_final_snapshot: true
'''

RETURN = r'''
db_instance_arn:
    description: The ARN of the database instance you just created or updated.
    returned: always
    type: string
'''

try:
    import botocore
    from botocore.exceptions import BotoCoreError, ClientError
except ImportError:
    pass  # handled by AnsibleAWSModule

from ansible.module_utils.aws.core import AnsibleAWSModule
from ansible.module_utils.aws.waiters import get_waiter


def instance_exists(client, module, params):
    if module.check_mode and module.params.get('state') == 'absent':
        return {'exists': False}
    try:
        response = client.describe_db_instances(
            DBInstanceIdentifier=params['DBInstanceIdentifier']
        )
    except client.exceptions.from_code('DBInstanceNotFound'):
        return {'exists': False}
    except (botocore.exceptions.ClientError, botocore.exceptions.BotoCoreError) as e:
        module.fail_json_aws(e, msg="Couldn't verify existence of graph database instance")

    return {'current_config': response['DBInstances'][0], 'exists': True}


def create_instance(client, module, params):
    if module.check_mode:
        module.exit_json(changed=True)
    try:
        response = client.create_db_instance(**params)
        waiter = client.get_waiter('db_instance_available')
        waiter.wait(
            DBInstanceIdentifier=params['DBInstanceIdentifier']
        )
    except (botocore.exceptions.ClientError, botocore.exceptions.BotoCoreError) as e:
        module.fail_json_aws(e, msg="Couldn't create graph database instance")

    return {'db_instance_arn': response['DBInstance']['DBInstanceArn'], 'changed': True}


def update_instance(client, module, params, instance_status):
    if module.check_mode:
        module.exit_json(changed=True)
    param_changed = []
    param_keys = list(params.keys())
    current_keys = list(instance_status['current_config'].keys())
    common_keys = set(param_keys) - (set(param_keys) - set(current_keys))
    for key in common_keys:
        if (params[key] != instance_status['current_config'][key]):
            param_changed.append(True)
        else:
            param_changed.append(False)

    if any(param_changed):
        try:
            response = client.modify_db_instance(**params)
            waiter = client.get_waiter('db_instance_available')
            waiter.wait(
                DBInstanceIdentifier=params['DBInstanceIdentifier']
            )
        except (botocore.exceptions.ClientError, botocore.exceptions.BotoCoreError) as e:
            module.fail_json_aws(e, msg="Couldn't update graph database instance")
        return {'db_instance_arn': response['DBInstance']['DBInstanceArn'], 'changed': True}
    else:
        return {'db_instance_arn': instance_status['current_config']['DBInstanceArn'], 'changed': False}


def delete_instance(client, module):
    if module.check_mode:
        module.exit_json(changed=True)
    try:
        params = {}
        params['DBInstanceIdentifier'] = module.params.get('name')
        if module.params.get('skip_final_snapshot'):
            params['SkipFinalSnapshot'] = module.params.get('skip_final_snapshot')
        if module.params.get('final_snapshot_id'):
            params['FinalDBSnapshotIdentifier'] = module.params.get('final_snapshot_id')
        response = client.delete_db_instance(**params)
        waiter = client.get_waiter('db_instance_deleted')
        waiter.wait(
            DBInstanceIdentifier=params['DBInstanceIdentifier']
        )
    except (botocore.exceptions.ClientError, botocore.exceptions.BotoCoreError) as e:
        module.fail_json_aws(e, msg="Couldn't delete graph database instance")

    return {'db_instance_arn': '', 'changed': True}


def main():
    module = AnsibleAWSModule(
        argument_spec={
            'name': dict(type='str', required=True),
            'state': dict(type='str', choices=['present', 'absent'], default='present'),
            'database_name': dict(type='str'),
            'instance_class': dict(type='str', required=True),
            'db_engine': dict(type='str', choices=['neptune'], default='neptune'),
            'master_username': dict(type='str'),
            'master_password': dict(type='str'),
            'db_security_groups': dict(type='list'),
            'vpc_security_groups': dict(type='list'),
            'availability_zone': dict(type='str'),
            'db_subnet_group': dict(type='str'),
            'maintenance_window': dict(type='str'),
            'parameter_group': dict(type='str'),
            'multi_az': dict(type='bool', default=False),
            'db_engine_version': dict(type='str'),
            'auto_minor_version_upgrade': dict(type='bool', default=True),
            'license_model': dict(type='str', choices=['license-included', 'bring-your-own-license', 'general-public-license']),
            'iops': dict(type='int'),
            'option_group': dict(type='str'),
            'publicly_accessible': dict(type='bool', default=False),
            'db_cluster': dict(type='str'),
            'tde_credential_arn': dict(type='str'),
            'tde_credential_password': dict(type='str'),
            'domain': dict(type='str'),
            'copy_tags_to_snapshot': dict(type='bool', default=False),
            'monitoring_interval': dict(type='int', choices=[0, 1, 5, 10, 15, 30, 60], default=0),
            'monitoring_role_arn': dict(type='str'),
            'domain_role_arn': dict(type='str'),
            'promotion_tier': dict(type='int', choices=[0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15]),
            'timezone': dict(type='str'),
            'enable_iam_auth': dict(type='bool', default=False),
            'enable_performance_insights': dict(type='bool', default=False),
            'performance_insights_kms_key': dict(type='str'),
            'enable_cloudwatch_logs_export': dict(type='list'),
            'skip_final_snapshot': dict(type='bool', default=False),
            'final_snapshot_id': dict(type='str'),
        },
        supports_check_mode=True,
    )

    result = {
        'changed': False,
        'db_instance_arn': ''
    }

    desired_state = module.params.get('state')

    params = {}
    if module.params.get('database_name'):
        params['DatabaseName'] = module.params.get('database_name')
    params['DBInstanceIdentifier'] = module.params.get('name')
    params['DBInstanceClass'] = module.params.get('instance_class')
    params['Engine'] = module.params.get('db_engine')
    if module.params.get('master_username'):
        params['MasterUsername'] = module.params.get('master_username')
    if module.params.get('master_password'):
        params['MasterUserPassword'] = module.params.get('master_password')
    if module.params.get('db_security_groups'):
        params['DBSecurityGroups'] = module.params.get('db_security_groups')
    if module.params.get('vpc_security_groups'):
        params['VpcSecurityGroupIds'] = module.params.get('vpc_security_groups')
    if module.params.get('availability_zone'):
        params['AvailabilityZone'] = module.params.get('availability_zone')
    if module.params.get('db_subnet_group'):
        params['DBSubnetGroupName'] = module.params.get('db_subnet_group')
    if module.params.get('maintenance_window'):
        params['PreferredMaintenanceWindow'] = module.params.get('maintenance_window')
    if module.params.get('parameter_group'):
        params['DBParameterGroupName'] = module.params.get('parameter_group')
    if module.params.get('multi_az'):
        params['MultiAZ'] = module.params.get('multi_az')
    if module.params.get('db_engine_version'):
        params['EngineVersion'] = module.params.get('db_engine_version')
    if module.params.get('auto_minor_version_upgrade'):
        params['AutoMinorVersionUpgrade'] = module.params.get('auto_minor_version_upgrade')
    if module.params.get('license_model'):
        params['LicenseModel'] = module.params.get('license_model')
    if module.params.get('iops'):
        params['Iops'] = module.params.get('iops')
    if module.params.get('option_group'):
        params['OptionGroupName'] = module.params.get('option_group')
    if module.params.get('publicly_accessible'):
        params['PubliclyAccessible'] = module.params.get('publicly_accessible')
    if module.params.get('db_cluster'):
        params['DBClusterIdentifier'] = module.params.get('db_cluster')
    if module.params.get('tde_credential_arn'):
        params['TdeCredentialArn'] = module.params.get('tde_credential_arn')
    if module.params.get('tde_credential_password'):
        params['TdeCredentialPassword'] = module.params.get('tde_credential_password')
    if module.params.get('domain'):
        params['Domain'] = module.params.get('domain')
    if module.params.get('copy_tags_to_snapshot'):
        params['CopyTagsToSnapshot'] = module.params.get('copy_tags_to_snapshot')
    if module.params.get('monitoring_interval'):
        params['MonitoringInterval'] = module.params.get('monitoring_interval')
    if module.params.get('monitoring_role_arn'):
        params['MonitoringRoleArn'] = module.params.get('monitoring_role_arn')
    if module.params.get('domain_role_arn'):
        params['DomainIAMRoleName'] = module.params.get('domain_role_arn')
    if module.params.get('promotion_tier'):
        params['PromotionTier'] = module.params.get('promotion_tier')
    if module.params.get('timezone'):
        params['Timezone'] = module.params.get('timezone')
    if module.params.get('enable_iam_auth'):
        params['EnableIAMDatabaseAuthentication'] = module.params.get('enable_iam_auth')
    if module.params.get('enable_performance_insights'):
        params['EnablePerformanceInsights'] = module.params.get('enable_performance_insights')
    if module.params.get('performance_insights_kms_key'):
        params['PerformanceInsightsKMSKeyId'] = module.params.get('performance_insights_kms_key')
    if module.params.get('enable_cloudwatch_logs_export'):
        params['EnableCloudwatchLogsExports'] = module.params.get('enable_cloudwatch_logs_export')

    client = module.client('neptune')

    instance_status = instance_exists(client, module, params)

    if desired_state == 'present':
        if not instance_status['exists']:
            result = create_instance(client, module, params)
        if instance_status['exists']:
            result = update_instance(client, module, params, instance_status)

    if desired_state == 'absent':
        if instance_status['exists']:
            result = delete_instance(client, module)

    module.exit_json(changed=result['changed'], db_instance_arn=result['db_instance_arn'])


if __name__ == '__main__':
    main()
