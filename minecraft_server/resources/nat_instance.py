from .abstract import Resource
from dataclasses import dataclass
from typing import List

from ..resources import IAMRole

from validated_dc import ValidatedDC

from aws_cdk import (
    aws_ec2 as ec2,
)
from constructs import Construct

'''
NOTE: NatInstance作るときにSecurityGroupを同時に作っている
（Vpc周りはVpcStackで完結させたかったので）
そのせいで、security_group.pyとほぼ一緒のコードを書いてしまっている、もうちょっときれいにできるかも
'''

@dataclass
class ResourceInfo(ValidatedDC):
    id: str
    availability_zone: str
    iam_instance_profile: str
    resource_name: str
    image_id: str
    instance_type: str
    source_dest_check: bool
    subnet_id: str
    eip_id: str
    _assign_name: str

class NatInstance(Resource):
    def __init__(self, 
    vpc: ec2.CfnVPC,
    iam_role: IAMRole,
    subnet_public_1a: ec2.CfnSubnet, 
    elastic_ip: ec2.CfnEIP) -> None:

        self._vpc = vpc

        self._resources = [
            {
                'id': 'Ec2InstanceNat',
                'availability_zone': 'ap-northeast-1a',
                'iam_instance_profile': iam_role.instance_profile_general_ec2.ref,
                'resource_name': 'EC2-NatIns-1a',
                # Nat Instance
                'image_id': 'ami-0a09a4184fb0fdc72',
                'instance_type': 't2.micro',
                'source_dest_check': False,
                'subnet_id': subnet_public_1a.ref,
                'eip_id': elastic_ip.ref,
                '_assign_name': 'natins_1a'
            },
        ]

        self.resources = [ResourceInfo(**resource) for resource in self._resources]

    def create_resources(self, scope: Construct):

        security_group = SecurityGroup(self._vpc)
        security_group.create_resources(scope)

        for resource_info in self.resources:
            
            nat_instance = ec2.CfnInstance(
                scope,
                resource_info.id,
                availability_zone=resource_info.availability_zone,
                iam_instance_profile=resource_info.iam_instance_profile,
                image_id=resource_info.image_id,
                instance_type=resource_info.instance_type,
                source_dest_check=resource_info.source_dest_check,
                security_group_ids=[security_group.natins.ref],
                subnet_id=resource_info.subnet_id,
                tags=[{'key': 'Name', 'value': self._create_resource_name(scope, resource_info.resource_name)}]
                )
            setattr(self,resource_info._assign_name, nat_instance)

            # EIPの付与
            ec2.CfnEIPAssociation(
                scope, 
                'NatInstanceAssociation', 
                eip=resource_info.eip_id,
                instance_id=nat_instance.ref)

@dataclass
class SecurityGroupIngressInfo(ValidatedDC):
    ip_protocol: str
    cidr_ip: str
    from_port: int
    to_port: int

@dataclass
class IngressInfo(ValidatedDC):
    id: str
    security_group_ingress_info: SecurityGroupIngressInfo

@dataclass
class NSResourceInfo(ValidatedDC):
    id: str
    group_description: str
    ingresses: List[IngressInfo]
    resource_name: str
    _assign_name: str

class SecurityGroup(Resource):
    def __init__(self, vpc: ec2.CfnVPC) -> None:
        self._vpc = vpc

        self._resources = [
            {
                'id': 'SecurityGroupNatInstance',
                'group_description': 'For NatInstance',
                'ingresses': [
                    {
                        'id': 'SecurityGroupIngressNatInstance1',
                        'security_group_ingress_info': {
                            'ip_protocol': 'tcp',
                            'cidr_ip': '10.8.0.0/16',
                            'from_port': 80,
                            'to_port': 80,
                        },
                    },
                    {
                        'id': 'SecurityGroupIngressNatInstance2',
                        'security_group_ingress_info': {
                            'ip_protocol': 'tcp',
                            'cidr_ip': '10.8.0.0/16',
                            'from_port': 443,
                            'to_port': 443,
                        },
                    },
                ],
                'resource_name': 'Sg-NatIns',
                '_assign_name': 'natins'
            },
        ]

        self.resources = [NSResourceInfo(**resource) for resource in self._resources]

    def create_resources(self, scope: Construct):
        for resource_info in self.resources:
            security_group = self.__create_security_group(scope, resource_info)
            setattr(self, resource_info._assign_name, security_group)

            self.__create_security_group_ingress(scope, security_group, resource_info)
    
    def __create_security_group(self, scope: Construct, resource_info: NSResourceInfo) -> ec2.CfnSecurityGroup:
        resource_name = self._create_resource_name(scope, resource_info.resource_name)
        return ec2.CfnSecurityGroup(
            scope, 
            resource_info.id,
            group_description=resource_info.group_description,
            group_name=resource_name,
            vpc_id=self._vpc.ref,
            tags=[{'key':'Name', 'value':resource_name}],
            )
    
    def __create_security_group_ingress(
        self, 
        scope: Construct, 
        security_group: ec2.CfnSecurityGroup, 
        resource_info: NSResourceInfo) -> None:

        for ingress_info in resource_info.ingresses:
            ec2.CfnSecurityGroupIngress(
                scope,
                ingress_info.id,
                ip_protocol=ingress_info.security_group_ingress_info.ip_protocol,
                cidr_ip=ingress_info.security_group_ingress_info.cidr_ip,
                from_port=ingress_info.security_group_ingress_info.from_port,
                to_port=ingress_info.security_group_ingress_info.to_port,
                group_id=security_group.ref,
                )