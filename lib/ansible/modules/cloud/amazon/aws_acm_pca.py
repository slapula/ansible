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
module: aws_acm_pca
short_description: Manage private certificate authorities on AWS Certificate Manager.
description:
    - Create, modify, and destroy private certificate authorities on AWS Certificate Manager.
version_added: "2.7"
requirements: [ 'botocore>=1.10.30', 'boto3' ]
author:
    - "Aaron Smith (@slapula)"
options:
  state:
    description:
    - Whether the resource should be present or absent.
    default: present
    choices: ['present', 'absent']
  ca_configuration:
    description:
    - Name and bit size of the private key algorithm, the name of the signing algorithm, and X.500 certificate subject information.
    required: true
    suboptions:
      key_algorithm:
        description:
        - Type of the public key algorithm and size, in bits, of the key pair that your key pair creates when it issues a certificate.
        required: true
        choices: ['RSA_2048', 'RSA_4096', 'EC_prime256v1', 'EC_secp384r1']
      signing_algorithm:
        description:
        - Name of the algorithm your private CA uses to sign certificate requests.
        required: true
        choices: ['SHA256WITHECDSA', 'SHA384WITHECDSA', 'SHA512WITHECDSA', 'SHA256WITHRSA', 'SHA384WITHRSA', 'SHA512WITHRSA']
      subject:
        description:
        - Structure that contains X.500 distinguished name information for your private CA.
        required: true
        suboptions:
          country:
            description:
            - Two digit code that specifies the country in which the certificate subject located.
          organization:
            description:
            - Legal name of the organization with which the certificate subject is affiliated.
          organizational_unit:
            description:
            - A subdivision or unit of the organization (such as sales or finance) with which the certificate subject is affiliated.
          name_qualifier:
            description:
            - Disambiguating information for the certificate subject.
          state:
            description:
            - State in which the subject of the certificate is located.
          common_name:
            description:
            - Fully qualified domain name (FQDN) associated with the certificate subject.
          serial_number:
            description:
            - The certificate serial number.
          locality:
            description:
            - The locality (such as a city or town) in which the certificate subject is located.
          title:
            description:
            - A title such as Mr. or Ms. which is pre-pended to the name to refer formally to the certificate subject.
          surname:
            description:
            - Family name. In the US and the UK for example, the surname of an individual is ordered last.
              In Asian cultures the surname is typically ordered first.
          given_name:
            description:
            - First name.
          initials:
            description:
            - Concatenation that typically contains the first letter of the `given_name` , the first letter of the
              middle name if one exists, and the first letter of the `surname` .
          pseudonym:
            description:
            - Typically a shortened version of a longer `given_name` .
          generation_qualifier:
            description:
            - Typically a qualifier appended to the name of an individual.
  revocation_configuration:
    description:
    - Contains a Boolean value that you can use to enable a certification revocation list (CRL) for the CA, the name of the S3 bucket
      to which ACM PCA will write the CRL, and an optional CNAME alias that you can use to hide the name of your bucket in the CRL
      Distribution Points extension of your CA certificate.
    suboptions:
      enabled:
        description:
        - Boolean value that specifies whether certificate revocation lists (CRLs) are enabled.
      expiration:
        description:
        - Number of days until a certificate expires.
      custom_cname:
        description:
        - Name inserted into the certificate CRL Distribution Points extension that enables the use of an alias for the CRL distribution point.
        - Use this value if you don't want the name of your S3 bucket to be public.
      s3_bucket:
        description:
        - Name of the S3 bucket that contains the CRL.
extends_documentation_fragment:
  - aws
  - ec2
'''

EXAMPLES = r'''
  - name: Create a new private certificate authority
    aws_acm_pca:
      state: present
      ca_configuration:
        key_algorithm: 'RSA_4096'
        signing_algorithm: 'SHA384WITHRSA'
        subject:
            country: 'US'
            organization: 'Example Ltd.'
            organizational_unit: 'IT'
            name_qualifier: 'example-pca'
            state: 'WI'
            common_name: 'example-pca.example.com'
            serial_number: '1234567890'
            locality: 'Rhinelander'
            title: 'Mr.'
            surname: 'Doe'
            given_name: 'John'
            initials: 'JD'
            pseudonym: 'Johnny'
            generation_qualifier: 'Sr.'
      revocation_configuration:
        enabled: true
        expiration: 365
        s3_bucket: 'pca-test-bucket'
'''

RETURN = r'''
pca_arn:
    description: The ARN of the private certificate authority you just created or updated.
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


def pca_exists(client, module, params):
    if module.check_mode and module.params.get('state') == 'absent':
        return {'exists': False}
    try:
        current_config = ''
        exists = False
        response = client.list_certificate_authorities()
        for i in response['CertificateAuthorities']:
            if module.params.get('ca_configuration').get('subject').get('common_name') == i['CertificateAuthorityConfiguration']['Subject']['CommonName']:
                current_config = i
                exists = True
    except (botocore.exceptions.ClientError, botocore.exceptions.BotoCoreError) as e:
        module.fail_json_aws(e, msg="Couldn't verify the existance of the private certificate authority")

    return {'current_config': current_config, 'exists': exists}


def create_pca(client, module, params):
    if module.check_mode:
        module.exit_json(changed=True)
    try:
        response = client.create_certificate_authority(**params)
        get_waiter(
            client, 'pca_available'
        ).wait(
            CertificateAuthorityArn=response['CertificateAuthorityArn']
        )
    except (botocore.exceptions.ClientError, botocore.exceptions.BotoCoreError) as e:
        module.fail_json_aws(e, msg="Couldn't create certificate authority")

    return {'pca_arn': response['CertificateAuthorityArn'], 'changed': True}


def update_pca(client, module, params, pca_status):
    if module.check_mode:
        module.exit_json(changed=True)
    param_changed = []
    param_keys = list(params.keys())
    current_keys = list(pca_status['current_config'].keys())
    common_keys = set(param_keys) - (set(param_keys) - set(current_keys))
    for key in common_keys:
        if (params[key] != pca_status['current_config'][key]):
            param_changed.append(True)
        else:
            param_changed.append(False)

    if any(param_changed):
        try:
            response = client.update_certificate_authority(**params)
            get_waiter(
                client, 'pca_available'
            ).wait(
                CertificateAuthorityArn=pca_status['current_config']['Arn']
            )
        except (botocore.exceptions.ClientError, botocore.exceptions.BotoCoreError) as e:
            module.fail_json_aws(e, msg="Couldn't update certificate authority")
        return {'pca_arn': pca_status['current_config']['Arn'], 'changed': True}
    else:
        return {'pca_arn': pca_status['current_config']['Arn'], 'changed': False}


def delete_pca(client, module, params, pca_status):
    if module.check_mode:
        module.exit_json(changed=True)
    try:
        response = client.delete_certificate_authority(
            CertificateAuthorityArn=pca_status['current_config']['Arn']
        )
        get_waiter(
            client, 'pca_deleted'
        ).wait(
            CertificateAuthorityArn=pca_status['current_config']['Arn']
        )
    except (botocore.exceptions.ClientError, botocore.exceptions.BotoCoreError) as e:
        module.fail_json_aws(e, msg="Couldn't delete certificate authority")

    return {'pca_arn': '', 'changed': True}


def main():
    module = AnsibleAWSModule(
        argument_spec={
            'state': dict(type='str', choices=['present', 'absent'], default='present'),
            'ca_configuration': dict(type='dict', required=True),
            'revocation_configuration': dict(type='dict'),
        },
        supports_check_mode=True,
    )

    if not module.botocore_at_least('1.10.30'):
        module.fail_json(msg="This module requires botocore >= 1.10.30")

    result = {
        'changed': False,
        'pca_arn': ''
    }

    desired_state = module.params.get('state')

    params = {}
    params['CertificateAuthorityConfiguration'] = {}
    params['CertificateAuthorityType'] = 'SUBORDINATE'
    params['CertificateAuthorityConfiguration'].update({
        'KeyAlgorithm': module.params.get('ca_configuration').get('key_algorithm')
    })
    params['CertificateAuthorityConfiguration'].update({
        'SigningAlgorithm': module.params.get('ca_configuration').get('signing_algorithm')
    })

    subject_params = {}
    if module.params.get('ca_configuration').get('subject').get('country'):
        subject_params['Country'] = module.params.get('ca_configuration').get('subject').get('country')
    if module.params.get('ca_configuration').get('subject').get('organization'):
        subject_params['Organization'] = module.params.get('ca_configuration').get('subject').get('organization')
    if module.params.get('ca_configuration').get('subject').get('organizational_unit'):
        subject_params['OrganizationalUnit'] = module.params.get('ca_configuration').get('subject').get('organizational_unit')
    if module.params.get('ca_configuration').get('subject').get('name_qualifier'):
        subject_params['DistinguishedNameQualifier'] = module.params.get('ca_configuration').get('subject').get('name_qualifier')
    if module.params.get('ca_configuration').get('subject').get('state'):
        subject_params['State'] = module.params.get('ca_configuration').get('subject').get('state')
    if module.params.get('ca_configuration').get('subject').get('common_name'):
        subject_params['CommonName'] = module.params.get('ca_configuration').get('subject').get('common_name')
    if module.params.get('ca_configuration').get('subject').get('serial_number'):
        subject_params['SerialNumber'] = module.params.get('ca_configuration').get('subject').get('serial_number')
    if module.params.get('ca_configuration').get('subject').get('locality'):
        subject_params['Locality'] = module.params.get('ca_configuration').get('subject').get('locality')
    if module.params.get('ca_configuration').get('subject').get('title'):
        subject_params['Title'] = module.params.get('ca_configuration').get('subject').get('title')
    if module.params.get('ca_configuration').get('subject').get('surname'):
        subject_params['Surname'] = module.params.get('ca_configuration').get('subject').get('surname')
    if module.params.get('ca_configuration').get('subject').get('given_name'):
        subject_params['GivenName'] = module.params.get('ca_configuration').get('subject').get('given_name')
    if module.params.get('ca_configuration').get('subject').get('initials'):
        subject_params['Initials'] = module.params.get('ca_configuration').get('subject').get('initials')
    if module.params.get('ca_configuration').get('subject').get('pseudonym'):
        subject_params['Pseudonym'] = module.params.get('ca_configuration').get('subject').get('pseudonym')
    if module.params.get('ca_configuration').get('subject').get('generation_qualifier'):
        subject_params['GenerationQualifier'] = module.params.get('ca_configuration').get('subject').get('generation_qualifier')
    params['CertificateAuthorityConfiguration'].update({
        'Subject': subject_params
    })

    if module.params.get('revocation_configuration'):
        revocation_params = {}
        revocation_params['Enabled'] = module.params.get('revocation_configuration').get('enabled')
        if module.params.get('revocation_configuration').get('expiration'):
            revocation_params['ExpirationInDays'] = module.params.get('revocation_configuration').get('expiration')
        if module.params.get('revocation_configuration').get('custom_cname'):
            revocation_params['CustomCname'] = module.params.get('revocation_configuration').get('custom_cname')
        if module.params.get('revocation_configuration').get('s3_bucket'):
            revocation_params['S3BucketName'] = module.params.get('revocation_configuration').get('s3_bucket')
        params['RevocationConfiguration'] = {}
        params['RevocationConfiguration'].update({
            'CrlConfiguration': revocation_params
        })

    client = module.client('acm-pca')

    pca_status = pca_exists(client, module, params)

    if desired_state == 'present':
        if not pca_status['exists']:
            result = create_pca(client, module, params)
        if pca_status['exists']:
            result = update_pca(client, module, params, pca_status)

    if desired_state == 'absent':
        if pca_status['exists']:
            result = delete_pca(client, module, params, pca_status)

    module.exit_json(changed=result['changed'], pca_arn=result['pca_arn'])


if __name__ == '__main__':
    main()
