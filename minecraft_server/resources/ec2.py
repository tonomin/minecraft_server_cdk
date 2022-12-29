from .abstract import Resource
from dataclasses import dataclass
from ..resources import (
    Subnet,
    IAMRole,
    SecurityGroup,
    ElasticIP,
)
from validated_dc import ValidatedDC
import base64

from aws_cdk import (
    aws_ec2 as ec2,
)
from constructs import Construct

@dataclass
class ResourceInfo(ValidatedDC):
    id: str
    availability_zone: str
    iam_instance_profile: str
    resource_name: str
    image_id: str
    instance_type: str
    subnet_id: str
    security_group_id: str
    _assign_name: str
    user_data_path: str = ''
    eip_id: str =''
    

class Ec2(Resource):
    def __init__(
        self, 
        subnet: Subnet, 
        iam_role: IAMRole, 
        security_group: SecurityGroup,
        elastic_ip: ElasticIP
        ) -> None:

        '''
                    {
                'id': 'Ec2InstanceAnsible1c',
                'availability_zone': 'ap-northeast-1c',
                'iam_instance_profile': iam_role.instance_profile_ansible_ec2.ref,
                'resource_name': 'EC2-Ansible-1c',
                # Amazon Linux2 k5.10
                'image_id': 'ami-0b5eea76982371e91',
                'instance_type': 't3.micro',
                'subnet_id': subnet.private_1c.ref,
                'security_group_id': security_group.ec2.ref,
                'user_data_path': './scripts/ansible/userData.sh',
                '_assign_name': 'ansible-1c'
            },
        '''
        self._resources = [
            {
                'id': 'Ec2InstanceMinecraft1a',
                'availability_zone': 'ap-northeast-1a',
                'iam_instance_profile': iam_role.instance_profile_general_ec2.ref,
                'resource_name': 'EC2-Minecraft-1a',
                # Alma Linux 8
                'image_id': 'ami-0b299c22ffb336d85',
                'instance_type': 't3.small',
                'subnet_id': subnet.public_1a.ref,
                'security_group_id': security_group.minecraft.ref,
                'eip_id': elastic_ip.minecraft_1a.ref,
                'user_data_path': './scripts/minecraft/userData.sh',
                '_assign_name': 'minecraft-1a'
            },
        ]

        self.resources = [ResourceInfo(**resource) for resource in self._resources]

    def create_resources(self, scope: Construct):
        for resource_info in self.resources:
            instance = self.__create_instance(scope, resource_info)
            setattr(self,resource_info._assign_name, instance)
    
    def __create_instance(self, scope: Construct, resource_info: ResourceInfo):
            if resource_info.user_data_path:
                with open(resource_info.user_data_path, 'rb') as f:
                    user_data_params = f.read()
                user_data = base64.b64encode(user_data_params).decode()
            else:
                user_data = None

            instance = ec2.CfnInstance(
                scope,
                resource_info.id,
                availability_zone=resource_info.availability_zone,
                iam_instance_profile=resource_info.iam_instance_profile,
                image_id=resource_info.image_id,
                instance_type=resource_info.instance_type,
                security_group_ids=[resource_info.security_group_id],
                subnet_id=resource_info.subnet_id,
                tags=[{'key': 'Name', 'value': self._create_resource_name(scope, resource_info.resource_name)}],
                user_data=user_data
                )
            
            if resource_info.eip_id:
                ec2.CfnEIPAssociation(
                scope, 
                resource_info.id+'Association', 
                eip=resource_info.eip_id,
                instance_id=instance.ref)

            keyName = scope.node.try_get_context('keyName')
            if keyName:
                instance.key_name = keyName
            
            return instance