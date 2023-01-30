from .abstract import Resource
from dataclasses import dataclass
from typing import List

from validated_dc import ValidatedDC

from aws_cdk import (
    aws_sns as sns,
    aws_iam as iam,
)
from constructs import Construct

@dataclass
class Statement(ValidatedDC):
    key: str
    value: dict

@dataclass
class TopicPolicy(ValidatedDC):
    id: str
    sid: str
    effect: iam.Effect
    principals: List[iam.ServicePrincipal]
    actions: List[str]
    statements: List[Statement]


@dataclass
class ResourceInfo(ValidatedDC):
    id: str
    topic_name: str
    topic_policy: TopicPolicy
    _assign_name: str

class SNS(Resource):
    def __init__(self, account:str) -> None:
        self._resources = [
            {
                'id': 'TopicBudgetAlerm',
                'topic_name': 'Global-SNS-BudgetAlerm1',
                'topic_policy': {
                    'id': 'TopicPolicyBudetAlerm',
                    'sid': 'AWSBudgetsSNSPublishingPermissions',
                    'effect': iam.Effect.ALLOW,
                    'principals': [iam.ServicePrincipal(service='budgets.amazonaws.com')],
                    'actions': ['SNS:Publish'],
                    'statements':[
                        {
                            'key': 'StringEquals',
                            'value': {"aws:SourceAccount": account}
                        },
                        {
                            'key': 'ArnLike', 
                            'value': {'aws:SourceArn': 'arn:aws:budgets::{}:*'.format(account)}
                        },
                    ]
                },
                '_assign_name': 'budget_alerm',
            }
        ]

        self.resources = [ResourceInfo(**resource) for resource in self._resources]

    def create_resources(self, scope: Construct):
        for resource_info in self.resources:
            topic = self.__create_topic (scope, resource_info)
            setattr(self, resource_info._assign_name, topic)
            
    def __create_topic(self, scope: Construct, resource_info: ResourceInfo) -> sns.Topic:
        topic = sns.Topic(
            scope,
            resource_info.id,
            topic_name=resource_info.topic_name,
        )

        policy_statement = iam.PolicyStatement(
            sid=resource_info.topic_policy.sid,
            effect=resource_info.topic_policy.effect,
            principals=resource_info.topic_policy.principals,
            actions=resource_info.topic_policy.actions,
            resources=[topic.topic_arn],
        )

        for statement in resource_info.topic_policy.statements:
            policy_statement.add_condition(statement.key,statement.value)

        policy_document = iam.PolicyDocument(
            assign_sids=True,
            statements=[policy_statement]
        )

        sns.TopicPolicy(
            scope, 
            resource_info.topic_policy.id,
            topics=[topic],
            policy_document=policy_document
        )

        return topic