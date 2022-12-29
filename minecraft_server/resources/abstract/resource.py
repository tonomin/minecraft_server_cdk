from abc import ABCMeta, abstractmethod

from constructs import Construct

class Resource(metaclass=ABCMeta):
    @abstractmethod
    def create_resources(scope: Construct) -> None:
        pass

    def _create_resource_name(self, scope: Construct, original_name: str) -> str:
        system_name = scope.node.try_get_context('systemName')
        env_type = scope.node.try_get_context('envType')
        resource_name_prefix = '{}-{}-'.format(system_name, env_type)

        return resource_name_prefix+original_name

