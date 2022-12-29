from .abstract import Resource
from dataclasses import dataclass
from typing import List

from validated_dc import ValidatedDC

from aws_cdk import (
    aws_ec2 as ec2,
)
from constructs import Construct

@dataclass
class AssociationInfo(ValidatedDC):
    id: str
    subnet_id: str

@dataclass
class ResourceInfo(ValidatedDC):
    id: str
    resource_name: str
    entry_inbound_id: str
    entry_outbound_id: str
    associations: List[AssociationInfo]
    _assign_name: str

class NetworkAcl(Resource):
    def __init__(
        self,
        vpc: ec2.CfnVPC,
        subnet_public_1a: ec2.CfnSubnet,
        subnet_public_1c: ec2.CfnSubnet,
        subnet_private_1a: ec2.CfnSubnet,
        subnet_private_1c: ec2.CfnSubnet,
        subnet_isolated_1a: ec2.CfnSubnet,
        subnet_isolated_1c: ec2.CfnSubnet,
        ) -> None:

        self._vpc = vpc
        self._subnet_public_1a = subnet_public_1a
        self._subnet_public_1c = subnet_public_1c
        self._subnet_private_1a = subnet_private_1a
        self._subnet_private_1c = subnet_private_1c
        self._subnet_isolated_1a = subnet_isolated_1a
        self._subnet_isolated_1c = subnet_isolated_1c

        self._resources = [
            {
                'id': 'NetworkAclPublic',
                'resource_name': 'NAcl-Public',
                'entry_inbound_id': 'NetworkAclEntryInboundPublic',
                'entry_outbound_id': 'NetworkAclEntryOutboundPublic',
                'associations': [
                    {
                        'id': 'NetworkAclAssociationPublic1a',
                        'subnet_id': self._subnet_public_1a.ref,
                    },
                    {
                        'id': 'NetworkAclAssociationPublic1c',
                        'subnet_id': self._subnet_public_1c.ref,
                    },
                ],
                '_assign_name': 'public'
            },
            {
                'id': 'NetworkAclPrivate',
                'resource_name': 'NAcl-Private',
                'entry_inbound_id': 'NetworkAclEntryInboundPrivate',
                'entry_outbound_id': 'NetworkAclEntryOutboundPrivate',
                'associations': [
                    {
                        'id': 'NetworkAclAssociationPrivate1a',
                        'subnet_id': self._subnet_private_1a.ref,
                    },
                    {
                        'id': 'NetworkAclAssociationPrivate1c',
                        'subnet_id': self._subnet_private_1c.ref,
                    },
                ],
                '_assign_name': 'private'
            },
            {
                'id': 'NetworkAclIsolated',
                'resource_name': 'NAcl-Isolated',
                'entry_inbound_id': 'NetworkAclEntryInboundIsolated',
                'entry_outbound_id': 'NetworkAclEntryOutboundIsolated',
                'associations': [
                    {
                        'id': 'NetworkAclAssociationIsolated1a',
                        'subnet_id': self._subnet_isolated_1a.ref,
                    },
                    {
                        'id': 'NetworkAclAssociationIsolated1c',
                        'subnet_id': self._subnet_isolated_1c.ref,
                    },
                ],
                '_assign_name': 'isolated'
            },
        ]

        self.resources = [ResourceInfo(**resource) for resource in self._resources]

    def create_resources(self, scope: Construct) -> None:

        for resource_info in self.resources:
            nacl = self.__create_network_acl(scope, resource_info)
            setattr(self, resource_info._assign_name, nacl)


    def __create_network_acl(self, scope: Construct, resource_info: ResourceInfo) -> ec2.CfnNetworkAcl:

        nacl = ec2.CfnNetworkAcl(
            scope,
            resource_info.id,
            vpc_id=self._vpc.ref,
            tags=[{'key':'Name', 'value':self._create_resource_name(scope, resource_info.resource_name)}],
        ) 

        self.__create_entry(scope, resource_info.entry_inbound_id, nacl)
        self.__create_entry(scope, resource_info.entry_outbound_id, nacl, True)

        for association_info in resource_info.associations:
            self.__create_association(scope, association_info, nacl)
        
        return nacl

    def __create_entry(self, scope: Construct, id: str, network_acl: ec2.CfnNetworkAcl, egress: bool = False) -> None:

        entry = ec2.CfnNetworkAclEntry(scope,
            id,
            network_acl_id=network_acl.ref,
            protocol=-1,
            rule_action='allow',
            rule_number=100,
            cidr_block='0.0.0.0/0',
            )
        
        if egress:
            entry.egress = True

    def __create_association(
        self, 
        scope: Construct, 
        association_info: AssociationInfo, 
        network_acl: ec2.CfnNetworkAcl
        ) -> None:

        ec2.CfnSubnetNetworkAclAssociation(
            scope,
            association_info.id,
            network_acl_id=network_acl.ref,
            subnet_id=association_info.subnet_id,
            )