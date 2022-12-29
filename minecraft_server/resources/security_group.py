from .abstract import Resource
from dataclasses import dataclass
from typing import List

from validated_dc import ValidatedDC

from aws_cdk import (
    aws_ec2 as ec2,
)
from constructs import Construct

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
class ResourceInfo(ValidatedDC):
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
                'id': 'SecurityGroupAlb',
                'group_description': 'For ALB',
                'ingresses': [
                    {
                        'id': 'SecurityGroupIngressAlb1',
                        'security_group_ingress_info': {
                            'ip_protocol': 'tcp',
                            'cidr_ip': '0.0.0.0/0',
                            'from_port': 80,
                            'to_port': 80,
                        },
                    },
                    {
                        'id': 'SecurityGroupIngressAlb2',
                        'security_group_ingress_info': {
                            'ip_protocol': 'tcp',
                            'cidr_ip': '0.0.0.0/0',
                            'from_port': 443,
                            'to_port': 443,
                        },
                    },
                ],
                'resource_name': 'Sg-ALB',
                '_assign_name': 'alb'
            },
            {
                'id': 'SecurityGroupEc2',
                'group_description': 'For Ec2',
                'ingresses': [
                    {
                        'id': 'SecurityGroupIngressEc21',
                        'security_group_ingress_info': {
                            'ip_protocol': 'tcp',
                            'cidr_ip': '0.0.0.0/0',
                            'from_port': 80,
                            'to_port': 80,
                        },
                    },
                ],
                'resource_name': 'Sg-EC2',
                '_assign_name': 'ec2'
            },
            {
                'id': 'SecurityGroupEc2Minecraft',
                'group_description': 'For Mincraft Server',
                'ingresses': [
                    {
                        'id': 'SecurityGroupIngressEc2Minecratf1',
                        'security_group_ingress_info': {
                            'ip_protocol': 'tcp',
                            'cidr_ip': '0.0.0.0/0',
                            'from_port': 25565,
                            'to_port': 25565,
                        },
                    },
                ],
                'resource_name': 'Sg-EC2-Minecraft',
                '_assign_name': 'minecraft'
            },
        ]

        self.resources = [ResourceInfo(**resource) for resource in self._resources]

    def create_resources(self, scope: Construct):
        for resource_info in self.resources:
            security_group = self.__create_security_group(scope, resource_info)
            setattr(self, resource_info._assign_name, security_group)

            self.__create_security_group_ingress(scope, security_group, resource_info)
    
    def __create_security_group(self, scope: Construct, resource_info: ResourceInfo) -> ec2.CfnSecurityGroup:
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
        resource_info: ResourceInfo) -> None:

        for ingress_info in resource_info.ingresses:
            ec2.CfnSecurityGroupIngress(
                scope,
                ingress_info.id,
                ip_protocol=ingress_info.security_group_ingress_info.ip_protocol,
                cidr_ip=ingress_info.security_group_ingress_info.cidr_ip,
                from_port=ingress_info.security_group_ingress_info.from_port,
                to_port=ingress_info.security_group_ingress_info.to_port,
                group_id=security_group.ref,
                # NOTE: sourceSecurityGroupIdとGroupIdってなにがちがうん？
                # source_security_group_id=security_group.ref
                )