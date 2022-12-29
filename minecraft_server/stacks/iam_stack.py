from aws_cdk import Stack
from constructs import Construct

from ..resources import (
    IAMRole,
)

class IAMStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # IAM
        self.iam_role = IAMRole(self.account)
        self.iam_role.create_resources(self)