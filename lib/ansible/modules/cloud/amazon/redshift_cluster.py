#!/usr/bin/python
# This file is part of Ansible
#
# Ansible is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Ansible is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Ansible.  If not, see <http://www.gnu.org/licenses/>.

from __future__ import absolute_import, division, print_function
__metaclass__ = type


ANSIBLE_METADATA = {
    'metadata_version': '1.1',
    'status': ['preview'],
    'supported_by': 'community'
}

DOCUMENTATION = '''
---
module: redshift_cluster
short_description: Create/Modify/Delete a Redshift cluster
description:
    - Module allows for the creation, modification, and deletion of a Redshift cluster
version_added: "2.5"
requirements: [ 'botocore', 'boto3' ]
author:
    - "Aaron Smith (@slapula)"
    - "Jens Carl (@j-carl), Hothead Games Inc."
options:
  state:
    description:
      - Specifies the overall state of the cluster.
    required: true
    choices: ['present', 'absent']
  cluster_identifier:
    description:
      - Redshift cluster identifier.
    required: true
  node_type:
    description:
      - The node type of the cluster. Must be specified when command=create.
    choices: ['ds1.xlarge', 'ds1.8xlarge', 'ds2.xlarge', 'ds2.8xlarge', 'dc1.large', 'dc1.8xlarge', 'dc2.large', 'dc2.8xlarge',
              'dw1.xlarge', 'dw1.8xlarge', 'dw2.large', 'dw2.8xlarge']
  username:
    description:
      - Master database username. Used only when command=create.
  password:
    description:
      - Master database password. Used only when command=create.
  cluster_type:
    description:
      - The type of cluster.
    choices: ['multi-node', 'single-node' ]
    default: 'single-node'
  db_name:
    description:
      - Name of the database.
    default: null
  availability_zone:
    description:
      - availability zone in which to launch cluster
    aliases: ['zone', 'aws_zone']
  number_of_nodes:
    description:
      - Number of nodes. Only used when cluster_type=multi-node.
    default: null
  cluster_subnet_group_name:
    description:
      - which subnet to place the cluster
    aliases: ['subnet']
  cluster_security_groups:
    description:
      - in which security group the cluster belongs
    default: null
    aliases: ['security_groups']
  vpc_security_group_ids:
    description:
      - VPC security group
    aliases: ['vpc_security_groups']
    default: null
  skip_final_cluster_snapshot:
    description:
      - skip a final snapshot before deleting the cluster. Used only when command=delete.
    aliases: ['skip_final_snapshot']
    default: false
    version_added: "2.4"
  final_cluster_snapshot_identifier:
    description:
      - identifier of the final snapshot to be created before deleting the cluster. If this parameter is provided,
        final_cluster_snapshot_identifier must be false. Used only when command=delete.
    aliases: ['final_snapshot_id']
    default: null
    version_added: "2.4"
  preferred_maintenance_window:
    description:
      - maintenance window
    aliases: ['maintance_window', 'maint_window']
    default: null
  cluster_parameter_group_name:
    description:
      - name of the cluster parameter group
    aliases: ['param_group_name']
    default: null
  automated_snapshot_retention_period:
    description:
      - period when the snapshot take place
    aliases: ['retention_period']
    default: null
  port:
    description:
      - which port the cluster is listining
    default: null
  cluster_version:
    description:
      - which version the cluster should have
    aliases: ['version']
    choices: ['1.0']
    default: null
  allow_version_upgrade:
    description:
      - flag to determinate if upgrade of version is possible
    aliases: ['version_upgrade']
    default: true
  publicly_accessible:
    description:
      - if the cluster is accessible publicly or not
    default: false
  encrypted:
    description:
      -  if the cluster is encrypted or not
    default: false
  elastic_ip:
    description:
      - if the cluster has an elastic IP or not
    default: null
extends_documentation_fragment:
  - aws
  - ec2
'''

EXAMPLES = '''
- name: create a redshift cluster
  redshift_cluster:
    state: 'present'
    cluster_identifier: 'testcluster'
    node_type: 'dc1.large'
    cluster_type: 'multi-node'
    number_of_nodes: 3
    username: 'dbadmin'
    password: "{{ dbadmin_password }}"

- name: modify that redshift cluster
  redshift_cluster:
    state: 'present'
    cluster_identifier: 'testcluster'
    node_type: 'dc2.xlarge'
    cluster_type: 'multi-node'
    number_of_nodes: 3
    username: 'dbadmin'
    password: "{{ dbadmin_password }}"

- name: delete that redshift cluster
  redshift_cluster:
    state: 'absent'
    cluster_identifier: 'testcluster'
    node_type: 'dc2.xlarge'
    cluster_type: 'multi-node'
    number_of_nodes: 3
    username: 'dbadmin'
    password: "{{ dbadmin_password }}"
'''

RETURN = '''
# For more information see U(http://boto3.readthedocs.io/en/latest/reference/services/redshift.html#Redshift.Client.describe_clusters)
---
cluster_identifier:
    description: Unique key to identify the cluster.
    returned: success
    type: string
    sample: "redshift-identifier"
node_type:
    description: The node type for nodes in the cluster.
    returned: success
    type: string
    sample: "ds2.xlarge"
cluster_status:
    description: Current state of the cluster.
    returned: success
    type: string
    sample: "available"
modify_status:
    description: The status of a modify operation.
    returned: optional
    type: string
    sample: ""
master_username:
    description: The master user name for the cluster.
    returned: success
    type: string
    sample: "admin"
db_name:
    description: The name of the initial database that was created when the cluster was created.
    returned: success
    type: string
    sample: "dev"
endpoint:
    description: The connection endpoint.
    returned: success
    type: string
    sample: {
        "address": "cluster-ds2.ocmugla0rf.us-east-1.redshift.amazonaws.com",
        "port": 5439
    }
cluster_create_time:
    description: The date and time that the cluster was created.
    returned: success
    type: string
    sample: "2016-05-10T08:33:16.629000+00:00"
automated_snapshot_retention_period:
    description: The number of days that automatic cluster snapshots are retained.
    returned: success
    type: int
    sample: 1
cluster_security_groups:
    description: A list of cluster security groups that are associated with the cluster.
    returned: success
    type: list
    sample: []
vpc_security_groups:
    description: A list of VPC security groups the are associated with the cluster.
    returned: success
    type: list
    sample: [
        {
            "status": "active",
            "vpc_security_group_id": "sg-12cghhg"
        }
    ]
cluster_paramater_groups:
    description: The list of cluster parameters that are associated with this cluster.
    returned: success
    type: list
    sample: [
        {
            "cluster_parameter_status_list": [
                {
                    "parameter_apply_status": "in-sync",
                    "parameter_name": "statement_timeout"
                },
                {
                    "parameter_apply_status": "in-sync",
                    "parameter_name": "require_ssl"
                }
            ],
            "parameter_apply_status": "in-sync",
            "parameter_group_name": "tuba"
        }
    ]
cluster_subnet_group_name:
    description: The name of the subnet group that is associated with the cluster.
    returned: success
    type: string
    sample: "redshift-subnet"
vpc_id:
    description: The identifier of the VPC the cluster is in, if the cluster is in a VPC.
    returned: success
    type: string
    sample: "vpc-1234567"
availibility_zone:
    description: The name of the Availability Zone in which the cluster is located.
    returned: success
    type: string
    sample: "us-east-1b"
preferred_maintenance_window:
    description: The weekly time range, in Universal Coordinated Time (UTC), during which system maintenance can occur.
    returned: success
    type: string
    sample: "tue:07:30-tue:08:00"
pending_modified_values:
    description: A value that, if present, indicates that changes to the cluster are pending.
    returned: success
    type: dict
    sample: {}
cluster_version:
    description: The version ID of the Amazon Redshift engine that is running on the cluster.
    returned: success
    type: string
    sample: "1.0"
allow_version_upgrade:
    description: >
      A Boolean value that, if true, indicates that major version upgrades will be applied
      automatically to the cluster during the maintenance window.
    returned: success
    type: boolean
    sample: true|false
number_of_nodes:
    description:  The number of compute nodes in the cluster.
    returned: success
    type: int
    sample: 12
publicly_accessible:
    description: A Boolean value that, if true , indicates that the cluster can be accessed from a public network.
    returned: success
    type: boolean
    sample: true|false
encrypted:
    description: Boolean value that, if true , indicates that data in the cluster is encrypted at rest.
    returned: success
    type: boolean
    sample: true|false
restore_status:
    description: A value that describes the status of a cluster restore action.
    returned: success
    type: dict
    sample: {}
hsm_status:
    description: >
      A value that reports whether the Amazon Redshift cluster has finished applying any hardware
      security module (HSM) settings changes specified in a modify cluster command.
    returned: success
    type: dict
    sample: {}
cluster_snapshot_copy_status:
    description: A value that returns the destination region and retention period that are configured for cross-region snapshot copy.
    returned: success
    type: dict
    sample: {}
cluster_public_keys:
    description: The public key for the cluster.
    returned: success
    type: string
    sample: "ssh-rsa anjigfam Amazon-Redshift\n"
cluster_nodes:
    description: The nodes in the cluster.
    returned: success
    type: list
    sample: [
        {
            "node_role": "LEADER",
            "private_ip_address": "10.0.0.1",
            "public_ip_address": "x.x.x.x"
        },
        {
            "node_role": "COMPUTE-1",
            "private_ip_address": "10.0.0.3",
            "public_ip_address": "x.x.x.x"
        }
    ]
elastic_ip_status:
    description: The status of the elastic IP (EIP) address.
    returned: success
    type: dict
    sample: {}
cluster_revision_number:
    description: The specific revision number of the database in the cluster.
    returned: success
    type: string
    sample: "1231"
tags:
    description: The list of tags for the cluster.
    returned: success
    type: list
    sample: []
kms_key_id:
    description: The AWS Key Management Service (AWS KMS) key ID of the encryption key used to encrypt data in the cluster.
    returned: success
    type: string
    sample: ""
enhanced_vpc_routing:
    description: An option that specifies whether to create the cluster with enhanced VPC routing enabled.
    returned: success
    type: boolean
    sample: true|false
iam_roles:
    description: List of IAM roles attached to the cluster.
    returned: success
    type: list
    sample: []
'''


from collections import defaultdict

try:
    import botocore
    import boto3
except ImportError:
    pass  # caught by AnsibleAWSModule

from ansible.module_utils.aws.core import AnsibleAWSModule
from ansible.module_utils.ec2 import boto3_conn, get_aws_connection_info, ec2_argument_spec, AWSRetry
from ansible.module_utils.ec2 import camel_dict_to_snake_dict, boto3_tag_list_to_ansible_dict


class RedshiftConnection(object):

    def __init__(self, module, region, **aws_connect_params):
        try:
            self.connection = boto3_conn(module, conn_type='client',
                                         resource='redshift', region=region,
                                         **aws_connect_params)
            self.module = module
        except Exception as e:
            module.fail_json(msg="Failed to connect to AWS: %s" % str(e))
        self.region = region

    def get_redshift_cluster(self, module):
        cluster_identifier = module.params.get('cluster_identifier')
        try:
            self.connection.describe_clusters(ClusterIdentifier=cluster_identifier)
            results = 'found'
        except self.connection.exceptions.ClusterNotFoundFault:
            results = 'missing'
        except (botocore.exceptions.ClientError, botocore.exceptions.BotoCoreError) as e:
            self.module.fail_json_aws(e, msg="Couldn't get Redshift Cluster")
        return results

    def create_redshift_cluster(self, module):
        cluster_identifier = module.params.get('cluster_identifier')
        node_type = module.params.get('node_type')
        username = module.params.get('username')
        password = module.params.get('password')

        args = {}
        for k, v in {'DBName':'db_name', 'ClusterType':'cluster_type',
                    'ClusterSecurityGroups':'cluster_security_groups',
                    'VpcSecurityGroupIds':'vpc_security_group_ids',
                    'ClusterSubnetGroupName':'cluster_subnet_group_name',
                    'AvailabilityZone':'availability_zone',
                    'PreferredMaintenanceWindow':'preferred_maintenance_window',
                    'ClusterParameterGroupName':'cluster_parameter_group_name',
                    'HsmClientCertificateIdentifier':'hsm_client_certificate_identifier',
                    'HsmConfigurationIdentifier':'hsm_configuration_identifier',
                    'AutomatedSnapshotRetentionPeriod':'automated_snapshot_retention_period',
                    'Port':'port', 'ClusterVersion':'cluster_version',
                    'AllowVersionUpgrade':'allow_version_upgrade', 'NumberOfNodes':'number_of_nodes',
                    'PubliclyAccessible':'publicly_accessible', 'Encrypted':'encrypted',
                    'ElasticIp':'elastic_ip', 'EnhancedVpcRouting':'enhanced_vpc_routing'}.items():
            if v in module.params and module.params.get(v) != None:
                args[k] = module.params.get(v)
        try:
            results = self.connection.create_cluster(
                ClusterIdentifier=cluster_identifier,
                NodeType=node_type,
                MasterUsername=username,
                MasterUserPassword=password,
                **args
            )
            cluster_available = self.connection.get_waiter('cluster_available')
            cluster_available.wait(ClusterIdentifier=cluster_identifier)
            raw_facts = self.connection.describe_clusters(ClusterIdentifier=cluster_identifier)['Clusters'][0]
        except (botocore.exceptions.ClientError, botocore.exceptions.BotoCoreError) as e:
            self.module.fail_json_aws(e, msg="Couldn't create Redshift Cluster")
        return results, raw_facts

    def delete_redshift_cluster(self, module):
        cluster_identifier = module.params.get('cluster_identifier')
        skip_final_cluster_snapshot = module.params.get('skip_final_cluster_snapshot')
        final_cluster_snapshot_identifier = module.params.get('final_cluster_snapshot_identifier')

        args = {}

        if module.params.get('skip_final_cluster_snapshot') == False:
            args['FinalClusterSnapshotIdentifier'] = module.params.get('final_cluster_snapshot_identifier')

        try:
            results = self.connection.delete_cluster(
                ClusterIdentifier=cluster_identifier,
                SkipFinalClusterSnapshot=skip_final_cluster_snapshot,
                **args
            )
            cluster_deleted = self.connection.get_waiter('cluster_deleted')
            cluster_deleted.wait(ClusterIdentifier=cluster_identifier)
        except self.connection.exceptions.ClusterNotFoundFault as e:
            self.module.fail_json_aws(e, msg="Couldn't find Redshift Cluster")
        except (botocore.exceptions.ClientError, botocore.exceptions.BotoCoreError) as e:
            self.module.fail_json_aws(e, msg="Couldn't get Redshift Cluster")
        return results

    def modify_redshift_cluster(self, module):
        results = []
        cluster_identifier = module.params.get('cluster_identifier')
        cluster_info = self.connection.describe_clusters(ClusterIdentifier=cluster_identifier)

        # Enhanced VPC routing changes must be made in a different request than other changes to the cluster
        vpc_args = {}
        if cluster_info['Clusters'][0]['EnhancedVpcRouting'] != module.params.get('enhanced_vpc_routing'):
            vpc_args['EnhancedVpcRouting'] = module.params.get('enhanced_vpc_routing')
        try:
            response = self.connection.modify_cluster(
                ClusterIdentifier=cluster_identifier,
                **vpc_args
            )
            cluster_available = self.connection.get_waiter('cluster_available')
            cluster_available.wait(ClusterIdentifier=cluster_identifier)
            results.append(response)
        except self.connection.exceptions.ClusterNotFoundFault as e:
            self.module.fail_json_aws(e, msg="Couldn't find Redshift Cluster")
        except (botocore.exceptions.ClientError, botocore.exceptions.BotoCoreError) as e:
            self.module.fail_json_aws(e, msg="Couldn't enhance Redshift Cluster")

        # The request to modify publicly accessible options for the cluster cannot be made in the same request as other modifications
        network_args = {}
        if cluster_info['Clusters'][0]['PubliclyAccessible'] != module.params.get('publicly_accessible'):
            network_args['ClusterType'] = module.params.get('publicly_accessible')
        if cluster_info['Clusters'][0]['ElasticIp'] != module.params.get('elastic_ip'):
            network_args['ElasticIp'] = module.params.get('elastic_ip')
        try:
            response = self.connection.modify_cluster(
                ClusterIdentifier=cluster_identifier,
                **network_args
            )
            cluster_available = self.connection.get_waiter('cluster_available')
            cluster_available.wait(ClusterIdentifier=cluster_identifier)
            results.append(response)
        except self.connection.exceptions.ClusterNotFoundFault as e:
            self.module.fail_json_aws(e, msg="Couldn't find Redshift Cluster")
        except (botocore.exceptions.ClientError, botocore.exceptions.BotoCoreError) as e:
            self.module.fail_json_aws(e, msg="Couldn't make Redshift Cluster publicly accessible")

        # When a resize operation is requested, no other modifications are allowed in the same request
        resize_args = {}
        if module.params.get('cluster_type') == 'single-node' and cluster_info['Clusters'][0]['NumberOfNodes'] > 1:
            resize_args['ClusterType'] = module.params.get('cluster_type')
        if module.params.get('cluster_type') == 'multi-node' and cluster_info['Clusters'][0]['NumberOfNodes'] != module.params.get('number_of_nodes'):
            resize_args['ClusterType'] = module.params.get('cluster_type')
            resize_args['NumberOfNodes'] = module.params.get('number_of_nodes')
        if cluster_info['Clusters'][0]['NodeType'] != module.params.get('node_type'):
            resize_args['ClusterType'] = module.params.get('cluster_type')
            resize_args['NodeType'] = module.params.get('node_type')
        try:
            response = self.connection.modify_cluster(
                ClusterIdentifier=cluster_identifier,
                **resize_args
            )
            cluster_available = self.connection.get_waiter('cluster_available')
            cluster_available.wait(ClusterIdentifier=cluster_identifier)
            results.append(response)
        except self.connection.exceptions.ClusterNotFoundFault as e:
            self.module.fail_json_aws(e, msg="Couldn't find Redshift Cluster")
        except (botocore.exceptions.ClientError, botocore.exceptions.BotoCoreError) as e:
            self.module.fail_json_aws(resize_args, msg="Couldn't resize Redshift Cluster")

        remaining_args = {}
        for k, v in {'MasterUserPassword':'password', 'ClusterSecurityGroups':'cluster_security_groups',
                    'VpcSecurityGroupIds':'vpc_security_group_ids',
                    'PreferredMaintenanceWindow':'preferred_maintenance_window',
                    'ClusterParameterGroupName':'cluster_parameter_group_name',
                    'HsmClientCertificateIdentifier':'hsm_client_certificate_identifier',
                    'HsmConfigurationIdentifier':'hsm_configuration_identifier',
                    'AutomatedSnapshotRetentionPeriod':'automated_snapshot_retention_period',
                    'ClusterVersion':'cluster_version', 'AllowVersionUpgrade':'allow_version_upgrade'}.items():
            if v in module.params and module.params.get(v) != None:
                remaining_args[k] = module.params.get(v)
        try:
            response = self.connection.modify_cluster(
                ClusterIdentifier=cluster_identifier,
                **remaining_args
            )
            cluster_available = self.connection.get_waiter('cluster_available')
            cluster_available.wait(ClusterIdentifier=cluster_identifier)
            results.append(response)
            raw_facts = self.connection.describe_clusters(ClusterIdentifier=cluster_identifier)['Clusters'][0]
        except self.connection.exceptions.ClusterNotFoundFault as e:
            self.module.fail_json_aws(e, msg="Couldn't find Redshift Cluster")
        except (botocore.exceptions.ClientError, botocore.exceptions.BotoCoreError) as e:
            self.module.fail_json_aws(e, msg="Couldn't modify Redshift Cluster")
        return results, raw_facts


def main():
    argument_spec = ec2_argument_spec()
    argument_spec.update(dict(
        state=dict(choices=['present', 'absent'], required=True),
        db_name=dict(require=False),
        cluster_identifier=dict(required=True),
        cluster_type=dict(choices=['multi-node', 'single-node'], default='single-node'),
        node_type=dict(choices=['ds1.xlarge', 'ds1.8xlarge', 'ds2.xlarge', 'ds2.8xlarge', 'dc1.large',
                                'dc2.large', 'dc1.8xlarge', 'dw1.xlarge', 'dw1.8xlarge', 'dw2.large',
                                'dw2.8xlarge'], required=True),
        username=dict(required=True),
        password=dict(no_log=True, required=True),
        cluster_security_groups=dict(aliases=['security_groups'], type='list'),
        vpc_security_group_ids=dict(aliases=['vpc_security_groups'], type='list'),
        cluster_subnet_group_name=dict(aliases=['subnet']),
        availability_zone=dict(aliases=['aws_zone', 'zone']),
        preferred_maintenance_window=dict(aliases=['maintance_window', 'maint_window']),
        cluster_parameter_group_name=dict(aliases=['param_group_name']),
        automated_snapshot_retention_period=dict(aliases=['retention_period']),
        port=dict(type='int'),
        cluster_version=dict(aliases=['version'], choices=['1.0']),
        allow_version_upgrade=dict(aliases=['version_upgrade'], type='bool', default=True),
        number_of_nodes=dict(type='int'),
        publicly_accessible=dict(type='bool', default=False),
        encrypted=dict(type='bool', default=False),
        hsm_client_certificate_identifier=dict(require=False),
        hsm_configuration_identifier=dict(require=False),
        elastic_ip=dict(required=False),
        tags=dict(type='dict', required=False),
        kms_key_id=dict(type='string', required=False),
        enhanced_vpc_routing=dict(type='bool', default=False),
        skip_final_cluster_snapshot=dict(aliases=['skip_final_snapshot'], type='bool', default=True),
        final_cluster_snapshot_identifier=dict(aliases=['final_snapshot_id'], required=False),
    ))

    module = AnsibleAWSModule(argument_spec=argument_spec,
                              supports_check_mode=True)

    region, _, aws_connect_params = get_aws_connection_info(module, boto3=True)
    connection = RedshiftConnection(module, region, **aws_connect_params)

    state = module.params.get('state')
    cluster_identifier = module.params.get('cluster_identifier')

    cluster_info = connection.get_redshift_cluster(module)

    if state == 'present' and cluster_info == 'missing':
        creation_result, creation_facts = connection.create_redshift_cluster(module)
        module.exit_json(changed=True, task_status={cluster_identifier: creation_facts})

    if state == 'present' and cluster_info == 'found':
        modify_result, modify_facts = connection.modify_redshift_cluster(module)
        module.exit_json(changed=True, task_status={cluster_identifier: modify_facts})

    if state == 'absent' and cluster_info == 'found':
        terminate_result = connection.delete_redshift_cluster(module)
        module.exit_json(changed=True, task_status={cluster_identifier: terminate_result})

    if state == 'absent' and cluster_info == 'missing':
        module.exit_json(changed=False, task_status={cluster_identifier: 'does not exist/already deleted'})

    module.exit_json(changed=False, task_status={cluster_identifier: 'unmodified'})


if __name__ == '__main__':
    main()
