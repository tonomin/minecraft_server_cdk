from aws_cdk import Stack
from constructs import Construct

from ..resources import (
    Budget,
)

from ..stacks import (
    SNSStack,
)

class BudgetStack(Stack):

    def __init__(
        self, 
        scope: Construct, 
        construct_id: str, 
        sns_stack: SNSStack,
        **kwargs) -> None:

        super().__init__(scope, construct_id, **kwargs)

        # Buget
        self.budget = Budget(sns_stack.sns)
        self.budget.create_resources(self)
