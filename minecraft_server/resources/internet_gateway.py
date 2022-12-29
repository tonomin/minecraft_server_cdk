from .abstract import Resource

from aws_cdk import (
    aws_ec2 as ec2,
)
from constructs import Construct

class InternetGateway(Resource):
    def __init__(self, vpc: ec2.CfnVPC) -> None:
        self._vpc=vpc

    def create_resources(self, scope: Construct):
        self.igw = ec2.CfnInternetGateway(
            scope, 
            'InternetGateway',
            tags=[{'key':'Name', 'value':self._create_resource_name(scope, 'IGW')}],
        )

        ec2.CfnVPCGatewayAttachment(
            scope, 
            'VpcGatewayAttachment',
            vpc_id=self._vpc.ref,
            internet_gateway_id=self.igw.ref,
        )