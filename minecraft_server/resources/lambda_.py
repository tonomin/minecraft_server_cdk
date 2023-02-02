from .abstract import Resource
from dataclasses import dataclass
from typing import List

from validated_dc import ValidatedDC

from ..resources import (
    IAMRole,
    SNS,
)

from aws_cdk import (
    aws_lambda as _lambda,
    aws_lambda_python_alpha as lambdapython,
    aws_lambda_event_sources as lambda_event_sources,
    aws_sns as sns_,
    aws_iam as iam,
    aws_ssm as ssm,
)

from constructs import Construct

@dataclass
class Env(ValidatedDC):
    name: str
    parameter_name: str


@dataclass
class ResourceInfo(ValidatedDC):
    id: str
    runtime: _lambda.Runtime
    entry: str
    index: str
    handler: str
    topic: sns_.CfnTopic
    role: iam.CfnRole
    envs: List[Env]
    resource_name: str
    _assign_name: str

class Lambda(Resource):
    def __init__(self, iam_role: IAMRole, sns: SNS) -> None:
        self._resources = [
            {
                'id': 'LambdaBudgetAlerm',
                'runtime': _lambda.Runtime.PYTHON_3_9,
                'entry': './scripts/lambda/budget_alerm',
                'index': 'index.py',
                'handler': 'handler',
                'topic': sns.budget_alerm,
                'role': iam_role.basic_lambda_exection,
                'envs':[
                    {
                        'name': 'NOTIFY_DISCORD_URL',
                        'parameter_name': '/minecraft-server/lambda/env/discord/budget-alerm-url',
                    }
                ],
                'resource_name': 'Lambda-BudgetAlerm',
                '_assign_name': 'budget_alerm',
            }
        ]
    
        self.resources = [ResourceInfo(**resource) for resource in self._resources]
    
    def create_resources(self, scope: Construct) -> None:
        for resource_info in self.resources:
            lambda_ = self.__create_lambda(scope, resource_info)
            setattr(self, resource_info._assign_name, lambda_)
    
    def __create_lambda(self, scope: Construct, resource_info: ResourceInfo) -> lambdapython.PythonFunction:
        lambda_ = lambdapython.PythonFunction(
            scope,
            resource_info.id,
            function_name=self._create_resource_name(scope, resource_info.resource_name),
            runtime=resource_info.runtime,
            entry=resource_info.entry,
            index=resource_info.index,
            handler=resource_info.handler,
            # FIXME: roleを指定すると動かない，要確認
            #role=resource_info.role,
            events=[lambda_event_sources.SnsEventSource(resource_info.topic)]
        )

        for env in resource_info.envs:
            lambda_.add_environment(env.name, ssm.StringParameter.value_for_string_parameter(scope,env.parameter_name))
        
        return lambda_