from aws_cdk import Stack
from constructs import Construct

from ..resources import (
    SecurityGroup,
    Ec2,
)
from ..stacks import (
    VpcStack,
    IAMStack
)

class Ec2Stack(Stack):

    def __init__(
        self, 
        scope: Construct, 
        construct_id: str, 
        vpc_stack: VpcStack, 
        iam_stack: IAMStack,
        **kwargs) -> None:

        super().__init__(scope, construct_id, **kwargs)

        # Security Group
        self.security_group = SecurityGroup(vpc_stack.vpc.vpc)
        self.security_group.create_resources(self)

        # EC2
        self.instance = Ec2(vpc_stack.subnet, iam_stack.iam_role, self.security_group, vpc_stack.elastic_ip)
        self.instance.create_resources(self)
