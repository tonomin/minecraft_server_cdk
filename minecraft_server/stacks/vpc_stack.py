from aws_cdk import Stack
from constructs import Construct

from ..resources import (
    Vpc,
    Subnet,
    InternetGateway,
    ElasticIP,
    RouteTable,
    NatInstance,
    NetworkAcl,
)

from ..stacks import IAMStack

class VpcStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, iam_stack: IAMStack, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # VPC
        self.vpc = Vpc()
        self.vpc.create_resources(self)

        # Subnet
        self.subnet = Subnet(self.vpc.vpc)
        self.subnet.create_resources(self)

        # Internet Gateway
        self.internet_gateway = InternetGateway(self.vpc.vpc)
        self.internet_gateway.create_resources(self)

        #Elastic IP
        self.elastic_ip = ElasticIP()
        self.elastic_ip.create_resources(self)

        # NatInstance
        self.nat_instance = NatInstance(
            self.vpc.vpc,
            iam_stack.iam_role,
            self.subnet.public_1a,
            self.elastic_ip.natins_1a,
            )
        self.nat_instance.create_resources(self)

        # Route Table
        self.route_table = RouteTable(
            self.vpc.vpc, 
            self.internet_gateway.igw, 
            self.subnet.public_1a, 
            self.subnet.public_1c,
            self.subnet.private_1a,
            self.subnet.private_1c,
            self.subnet.isolated_1a,
            self.subnet.isolated_1c,
            self.nat_instance.natins_1a)
        self.route_table.create_resources(self)

        # Network ACL
        self.network_acl = NetworkAcl(
            self.vpc.vpc,
            self.subnet.public_1a, 
            self.subnet.public_1c,
            self.subnet.private_1a,
            self.subnet.private_1c,
            self.subnet.isolated_1a,
            self.subnet.isolated_1c,
        )
        self.network_acl.create_resources(self)
