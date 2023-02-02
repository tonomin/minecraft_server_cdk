from aws_cdk import Stack
from constructs import Construct

from ..resources import (
    Lambda,
)
from ..stacks import (
    IAMStack,
    SNSStack,
)

class LambdaStack(Stack):

    def __init__(
        self, 
        scope: Construct, 
        construct_id: str, 
        iam_stack: IAMStack,
        sns_stack: SNSStack,
        **kwargs) -> None:

        super().__init__(scope, construct_id, **kwargs)

        # Lambda
        self.instance = Lambda(iam_stack.iam_role, sns_stack.sns)
        self.instance.create_resources(self)
