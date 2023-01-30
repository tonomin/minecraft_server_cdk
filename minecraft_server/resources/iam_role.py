from .abstract import Resource
from dataclasses import dataclass
from typing import List

from validated_dc import ValidatedDC

from aws_cdk import (
    aws_iam as iam,
)
from constructs import Construct

@dataclass
class PolicyStatementInfo(ValidatedDC):
    effect: iam.Effect
    principals: List[iam.ServicePrincipal]
    actions: List[str]

@dataclass
class ResourceInfo(ValidatedDC):
    id: str
    policy_statement_info: PolicyStatementInfo
    managed_policy_arns: List[str]
    resource_name: str
    _assign_name: str
    instance_profile_id: str
    _instance_profile_assign_name: str

class IAMRole(Resource):
    def __init__(self, account:str) -> None:
        self._resources = [
            {
                'id': 'RoleGeneralEc2',
                'policy_statement_info': {
                    'effect': iam.Effect.ALLOW,
                    'principals': [iam.ServicePrincipal('ec2.amazonaws.com')],
                    'actions': ['sts:AssumeRole'],
                },
                'managed_policy_arns': [
                    'arn:aws:iam::aws:policy/AmazonSSMManagedInstanceCore',
                    'arn:aws:iam::aws:policy/CloudWatchAgentServerPolicy'
                    ],
                'resource_name': 'Role-GeneralEc2',
                '_assign_name': 'general_ec2',
                'instance_profile_id': 'InstanceProfileGeneralEc2',
                '_instance_profile_assign_name': 'instance_profile_general_ec2',
            },
            {
                'id': 'RoleAnsibleEc2',
                'policy_statement_info': {
                    'effect': iam.Effect.ALLOW,
                    'principals': [iam.ServicePrincipal('ec2.amazonaws.com')],
                    'actions': ['sts:AssumeRole'],
                },
                # MinecraftServiceEc2PemAccess は事前に作成済み（EC2のキーペア取得用）
                'managed_policy_arns': [
                    'arn:aws:iam::aws:policy/AmazonSSMFullAccess',
                    'arn:aws:iam::{}:policy/MinecraftServiceEc2PemAccess'.format(account)
                    ],
                'resource_name': 'Role-AnsibleEc2',
                '_assign_name': 'ansible_ec2',
                'instance_profile_id': 'InstanceProfileAnsibleEc2',
                '_instance_profile_assign_name': 'instance_profile_ansible_ec2',
            },
        ]

        self.resources = [ResourceInfo(**resource) for resource in self._resources]

    def create_resources(self, scope: Construct):
        for resource_info in self.resources:
            role = self.__create_role(scope, resource_info)
            setattr(self, resource_info._assign_name, role)

            instance_profile = iam.CfnInstanceProfile(
                scope,
                resource_info.instance_profile_id,
                roles=[role.ref],
                instance_profile_name=role.role_name
                )
            setattr(self, resource_info._instance_profile_assign_name, instance_profile)

    def __create_role(self, scope: Construct, resource_info: ResourceInfo) -> iam.PolicyStatement:
        policy_statement = iam.PolicyStatement(
            effect=resource_info.policy_statement_info.effect,
            principals=resource_info.policy_statement_info.principals,
            actions=resource_info.policy_statement_info.actions,
            )
        policy_document = iam.PolicyDocument(statements=[policy_statement])

        return iam.CfnRole(
            scope,
            resource_info.id,
            assume_role_policy_document=policy_document,
            managed_policy_arns=resource_info.managed_policy_arns,
            role_name=self._create_resource_name(scope, resource_info.resource_name),
            )
        
        