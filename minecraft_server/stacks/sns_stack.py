from aws_cdk import Stack
from constructs import Construct

from ..resources import (
    SNS
)

class SNSStack(Stack):

    def __init__(
        self, 
        scope: Construct, 
        construct_id: str, 
        **kwargs) -> None:

        super().__init__(scope, construct_id, **kwargs)

        # SNS
        self.sns = SNS(self.account)
        self.sns.create_resources(self)
