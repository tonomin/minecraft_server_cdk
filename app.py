#!/usr/bin/env python3
import os

import aws_cdk as cdk
from aws_cdk import Tags

from minecraft_server.stacks import (
    VpcStack,
    IAMStack,
    Ec2Stack,
    SNSStack,
    BudgetStack,

)

app = cdk.App()

iam_stack = IAMStack(app, "IAMStack",
    env=cdk.Environment(
        account=os.getenv('CDK_DEFAULT_ACCOUNT'), 
        region=os.getenv('CDK_DEFAULT_REGION')
        ),
)

vpc_stack = VpcStack(app, "VpcStack", iam_stack,
    env=cdk.Environment(
        account=os.getenv('CDK_DEFAULT_ACCOUNT'), 
        region=os.getenv('CDK_DEFAULT_REGION')
        ),
)

ec2_stack = Ec2Stack(app, "Ec2Stack", vpc_stack, iam_stack,
    env=cdk.Environment(
        account=os.getenv('CDK_DEFAULT_ACCOUNT'), 
        region=os.getenv('CDK_DEFAULT_REGION')
        ),
)

sns_stack = SNSStack(app, 'SNSStack',
    env=cdk.Environment(
        account=os.getenv('CDK_DEFAULT_ACCOUNT'), 
        region=os.getenv('CDK_DEFAULT_REGION')
        ),
)

budget_stack = BudgetStack(app, 'BudgetStack', sns_stack,
    env=cdk.Environment(
        account=os.getenv('CDK_DEFAULT_ACCOUNT'), 
        region=os.getenv('CDK_DEFAULT_REGION')
        ),
)

# Stack内の全リソースにタグ付け
env_type = app.node.try_get_context("envType")
system_name = app.node.try_get_context("systemName")

Tags.of(vpc_stack).add("CreatedBy", "CDK")
Tags.of(vpc_stack).add("Env", env_type)
Tags.of(vpc_stack).add("SystemName", system_name)
Tags.of(iam_stack).add("CreatedBy", "CDK")
Tags.of(iam_stack).add("Env", env_type)
Tags.of(iam_stack).add("SystemName", system_name)
Tags.of(ec2_stack).add("CreatedBy", "CDK")
Tags.of(ec2_stack).add("Env", env_type)
Tags.of(ec2_stack).add("SystemName", system_name)
app.synth()
