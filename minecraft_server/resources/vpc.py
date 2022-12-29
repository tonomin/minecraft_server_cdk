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
    resource_name: str
    _assign_name: str

class Vpc(Resource):
    def __init__(self) -> None:
        self._resources = [
            {
                'id': 'Vpc',
                'cidr_block': '10.8.0.0/16',
                'resource_name': 'Vpc',
                '_assign_name': 'vpc',
            }
        ]

        self.resources = [ResourceInfo(**resource) for resource in self._resources]

    def create_resources(self, scope: Construct):
        for resource_info in self.resources:
            vpc = self.__create_vpc(scope, resource_info)
            setattr(self, resource_info._assign_name, vpc)
    
    def __create_vpc(self, scope: ec2.CfnVPC, resource_info: ResourceInfo) -> ec2.CfnVPC:
        return ec2.CfnVPC(scope,
            resource_info.id,
            cidr_block=resource_info.cidr_block,
            tags=[{'key':'Name', 'value':self._create_resource_name(scope, resource_info.resource_name)}],
        )