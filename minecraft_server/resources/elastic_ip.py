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
    domain: str
    resource_name: str
    _assign_name: str

class ElasticIP(Resource):
    def __init__(self) -> None:
        self._resources = [
            {
                'id': 'ElasticIpNatins1a',
                'domain': 'vpc',
                'resource_name': 'EIP-NatIns-1a',
                '_assign_name': 'natins_1a'
            },
            {
                'id': 'ElasticIpMinecraft1a',
                'domain': 'vpc',
                'resource_name': 'EIP-Minecraft-1a',
                '_assign_name': 'minecraft_1a'
            },
        ]

        self.resources = [ResourceInfo(**resource) for resource in self._resources]

    def create_resources(self, scope: Construct):
        for resource_info in self.resources:
            ngw = ec2.CfnEIP(
                scope,
                resource_info.id,
                domain=resource_info.domain,
                tags=[{'key':'Name', 'value':self._create_resource_name(scope, resource_info.resource_name)}],
                )
            setattr(self, resource_info._assign_name, ngw)
