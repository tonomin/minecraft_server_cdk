from .abstract import Resource
from dataclasses import dataclass

from validated_dc import ValidatedDC

from aws_cdk import (
    aws_ec2 as ec2,
)
from constructs import Construct

@dataclass
class ResourceInfo(ValidatedDC):
    id: str
    cidr_block: str
    availability_zone: str
    resource_name: str
    _assign_name: str

class Subnet(Resource):
    def __init__(self, vpc: ec2.CfnVPC):
        self._vpc = vpc

        self._resources = [
            {
                'id': 'SubnetPublic1a',
                'cidr_block': '10.8.3.0/24',
                'availability_zone': 'ap-northeast-1a',
                'resource_name': 'Subnet-Public-1a',
                '_assign_name': 'public_1a'
            },
            {
                'id': 'SubnetPublic1c',
                'cidr_block': '10.8.4.0/24',
                'availability_zone': 'ap-northeast-1c',
                'resource_name': 'Subnet-Public-1c',
                '_assign_name': 'public_1c'
            },
            {
                'id': 'SubnetPrivate1a',
                'cidr_block': '10.8.5.0/24',
                'availability_zone': 'ap-northeast-1a',
                'resource_name': 'Subnet-Private-1a',
                '_assign_name': 'private_1a'
            },
            {
                'id': 'SubnetPrivate1c',
                'cidr_block': '10.8.6.0/24',
                'availability_zone': 'ap-northeast-1c',
                'resource_name': 'Subnet-Private-1c',
                '_assign_name': 'private_1c'
            },
            {
                'id': 'SubnetIsolated1a',
                'cidr_block': '10.8.7.0/24',
                'availability_zone': 'ap-northeast-1a',
                'resource_name': 'Subnet-Isolated-1a',
                '_assign_name': 'isolated_1a'
            },
            {
                'id': 'SubnetIsolated1c',
                'cidr_block': '10.8.8.0/24',
                'availability_zone': 'ap-northeast-1c',
                'resource_name': 'Subnet-Isolated-1c',
                '_assign_name': 'isolated_1c'
            },
        ]

        self.resources = [ResourceInfo(**resource) for resource in self._resources]

    def create_resources(self, scope: Construct) -> None:
        for resource_info in self.resources:
            subnet = self.__create_subnet(scope, resource_info)
            setattr(self, resource_info._assign_name, subnet)

    
    def __create_subnet(self, scope: Construct, resource_info: ResourceInfo) -> ec2.CfnSubnet:
        return ec2.CfnSubnet(
            scope, 
            resource_info.id,
            cidr_block=resource_info.cidr_block,
            vpc_id=self._vpc.ref,
            availability_zone=resource_info.availability_zone,
            tags=[{'key':'Name', 'value':self._create_resource_name(scope, resource_info.resource_name)}]
            )