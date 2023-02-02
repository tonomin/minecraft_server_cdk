from .abstract import Resource
from dataclasses import dataclass
from typing import List

from validated_dc import ValidatedDC

from ..resources import (
    SNS,
)

from aws_cdk import (
    aws_budgets as budgets,
)
from constructs import Construct

@dataclass
class BudgetLimit(ValidatedDC):
    amount: int
    unit: str

@dataclass
class BudgetDataProps(ValidatedDC):
    buget_type: str
    time_unit: str
    budget_limit: BudgetLimit
    budget_name: str

@dataclass
class Notification(ValidatedDC):
    comparison_operator: str
    notification_type: str
    threshold: int
    threshold_type: str

@dataclass
class Subscriber(ValidatedDC):
    subscription_type: str
    address: str

@dataclass
class NotificationsWithSubscriber(ValidatedDC):
    notification: Notification
    subscribers: List[Subscriber]

@dataclass
class ResourceInfo(ValidatedDC):
    id: str
    budget_data_props: BudgetDataProps
    notifications_with_subscribers: List[NotificationsWithSubscriber]
    _assign_name: str

class Budget(Resource):
    def __init__(self, sns: SNS) -> None:
        self._resources = [
            {
                'id': 'BudgetAllInAccount',
                'budget_data_props': {
                    'buget_type': 'COST',
                    'time_unit': 'MONTHLY',
                    'budget_limit': {
                        'amount': 50,
                        'unit': 'USD',
                    },

                    'budget_name': 'Global-Budget-Monthly',
                },
                'notifications_with_subscribers': [
                    {
                        'notification': {
                            'comparison_operator': 'GREATER_THAN',
                            'notification_type': 'ACTUAL',
                            'threshold': 1,
                            'threshold_type': 'PERCENTAGE',
                        },
                        'subscribers': [
                            {
                                'subscription_type': 'SNS',
                                'address': sns.budget_alerm.topic_arn,
                            },
                        ],
                    }
                ],
                '_assign_name': 'all_in_account',
            }
        ]
    
        self.resources = [ResourceInfo(**resource) for resource in self._resources]

    def create_resources(self, scope: Construct):
        for resource_info in self.resources:
            budget = self.__create_budget(scope, resource_info)
            setattr(self, resource_info._assign_name, budget)

    def __create_budget(self, scope: Construct, resource_info: ResourceInfo):
        buget_data_props = budgets.CfnBudget.BudgetDataProperty(
            budget_type=resource_info.budget_data_props.buget_type,
            time_unit=resource_info.budget_data_props.time_unit,
            budget_limit=budgets.CfnBudget.SpendProperty(
                amount=resource_info.budget_data_props.budget_limit.amount,
                unit=resource_info.budget_data_props.budget_limit.unit,
                ),
            budget_name=resource_info.budget_data_props.budget_name,
            )

        notifications_with_subscribers_props = []
        for notifications_with_subscriber in resource_info.notifications_with_subscribers:
            notifications_with_subscribers_props.append(
                budgets.CfnBudget.NotificationWithSubscribersProperty(
                    notification=budgets.CfnBudget.NotificationProperty(
                        comparison_operator=notifications_with_subscriber.notification.comparison_operator,
                        notification_type=notifications_with_subscriber.notification.notification_type,
                        threshold=notifications_with_subscriber.notification.threshold,
                        threshold_type=notifications_with_subscriber.notification.threshold_type,
                    ),
                    subscribers=[
                        budgets.CfnBudget.SubscriberProperty(
                            address=subscriber.address, 
                            subscription_type=subscriber.subscription_type,
                        ) 
                        for subscriber in notifications_with_subscriber.subscribers
                    ]
                )
            )

        return budgets.CfnBudget(
            scope,
            resource_info.id,
            budget=buget_data_props,
            notifications_with_subscribers=notifications_with_subscribers_props
            )
        
       
