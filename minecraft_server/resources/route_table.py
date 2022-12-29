from .abstract import Resource
from dataclasses import dataclass
from typing import List

from validated_dc import ValidatedDC

from aws_cdk import (
    aws_ec2 as ec2,
)
from constructs import Construct

@dataclass
class RouteInfo(ValidatedDC):
    id: str
    destination_cidr_block: str
    gateway_id: str = ''
    nat_gateway_id: str = ''
    instance_id: str = ''

@dataclass
class AssociationInfo(ValidatedDC):
    id: str
    subnet_id: str

@dataclass
class ResourceInfo(ValidatedDC):
    id: str
    resource_name: str
    routes: List[RouteInfo]
    associations: List[AssociationInfo]
    _assign_name: str

class RouteTable(Resource):

    def __init__(
        self, 
        vpc: ec2.CfnVPC, 
        igw: ec2.CfnInternetGateway,
        subnet_public_1a: ec2.CfnSubnet,
        subnet_public_1c: ec2.CfnSubnet,
        subnet_private_1a: ec2.CfnSubnet,
        subnet_private_1c: ec2.CfnSubnet,
        subnet_isolated_1a: ec2.CfnSubnet,
        subnet_isolated_1c: ec2.CfnSubnet,
        nat_instance_1a: ec2.CfnInstance,
        ) -> None:

        self._vpc = vpc

        self._resources = [
            {
                'id': 'RouteTablePublic',
                'resource_name': 'Rtb-Public',
                'routes': [
                    {
                        'id': 'RoutePublic',
                        'destination_cidr_block': '0.0.0.0/0',
                        'gateway_id': igw.ref,
                    },
                ],
                'associations': [
                    {
                        'id': 'AssociationPublic1a',
                        'subnet_id': subnet_public_1a.ref,
                    },
                    {
                        'id': 'AssociationPublic1c',
                        'subnet_id': subnet_public_1c.ref,
                    },
                ],
                '_assign_name': 'public',
            },
            {
                'id': 'RouteTablePrivate1a',
                'resource_name': 'Rtb-Private-1a',
                'routes': [
                    {
                        'id': 'RoutePrivate1a',
                        'destination_cidr_block': '0.0.0.0/0',
                        'instance_id': nat_instance_1a.ref,
                    },
                ],
                'associations': [
                    {
                        'id': 'AssociationPrivate1a',
                        'subnet_id': subnet_private_1a.ref,
                    },
                ],
                '_assign_name': 'private_1a',
            },
            {
                'id': 'RouteTablePrivate1c',
                'resource_name': 'Rtb-Private-1c',
                'routes': [
                    {
                        'id': 'RoutePrivate1c',
                        'destination_cidr_block': '0.0.0.0/0',
                        'instance_id': nat_instance_1a.ref,
                    },
                ],
                'associations': [
                    {
                        'id': 'AssociationPrivate1c',
                        'subnet_id': subnet_private_1c.ref,
                    },
                ],
                '_assign_name': 'private_1c',
            },
            {
                'id': 'RouteTableIsolates',
                'resource_name': 'Rtb-Isolated',
                'routes': [],
                'associations': [
                    {
                        'id': 'AssociationIsolated1a',
                        'subnet_id': subnet_isolated_1a.ref,
                    },
                    {
                        'id': 'AssociationIsolated1c',
                        'subnet_id': subnet_isolated_1c.ref,
                    },
                ],
                '_assign_name': 'isolated',
            },
        ]

        self.resources = [ResourceInfo(**resource) for resource in self._resources]

    def create_resources(self, scope: Construct) -> None:
        for resource_info in self.resources:
            route_table = self.__create_route_table(scope, resource_info)
            setattr(self, resource_info._assign_name, route_table)
        
    def __create_route_table(self, scope: Construct, resource_info: ResourceInfo) -> ec2.CfnRouteTable:
        route_table = ec2.CfnRouteTable(
            scope,
            resource_info.id,
            vpc_id=self._vpc.ref,
            tags=[{'key':'Name', 'value':self._create_resource_name(scope, resource_info.resource_name)}],
        )

        for route_info in resource_info.routes:
            self.__create_route(scope, route_info, route_table)
        
        for association_info in resource_info.associations:
            self.__create_association(scope, association_info, route_table)

        return route_table
    
    def __create_route(
        self, 
        scope: Construct, 
        route_info: RouteInfo, 
        route_table: ec2.CfnRouteTable
        ) -> None:

        route = ec2.CfnRoute(
            scope,
            route_info.id,
            route_table_id=route_table.ref,
            destination_cidr_block=route_info.destination_cidr_block,
            
        )

        if route_info.gateway_id:
            route.gateway_id = route_info.gateway_id
        elif route_info.nat_gateway_id:
            route.nat_gateway_id = route_info.nat_gateway_id
        elif route_info.instance_id:
            route.instance_id = route_info.instance_id
    
    def __create_association(
        self,
        scope: Construct,
        association_info: AssociationInfo,
        route_table: ec2.CfnRouteTable) -> None:

        ec2.CfnSubnetRouteTableAssociation(
            scope,
            association_info.id,
            route_table_id=route_table.ref,
            subnet_id=association_info.subnet_id
            )