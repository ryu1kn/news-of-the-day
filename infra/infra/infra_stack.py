import os

from aws_cdk import (
    Stack,
    CfnTag,
    Tags,
    aws_iam,
    aws_redshiftserverless as redshiftserverless
)
from constructs import Construct


class InfraStack(Stack):

    tag_system = CfnTag(key="system", value="news-of-the-day")

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        role = aws_iam.Role(
            self,
        "RedshiftRole",
            role_name="newsoftheday-redshift-serverless-role",

            # https://docs.aws.amazon.com/redshift/latest/mgmt/serverless-iam.html#serverless-security-other-services
            managed_policies=[aws_iam.ManagedPolicy.from_aws_managed_policy_name("AmazonRedshiftAllCommandsFullAccess")],
            assumed_by=aws_iam.CompositePrincipal(
                aws_iam.ServicePrincipal("redshift-serverless.amazonaws.com"),
                aws_iam.ServicePrincipal("redshift.amazonaws.com"),
            )
        )
        Tags.of(role).add(self.tag_system.key, self.tag_system.value)

        cfn_namespace = redshiftserverless.CfnNamespace(self, "Namespace",
            namespace_name="newsoftheday-namespace",

            # Temporary settings for spiking
            admin_username=os.environ['REDSHIFT_ADMIN_USERNAME'],
            admin_user_password=os.environ['REDSHIFT_ADMIN_USER_PASSWORD'],

            db_name="newsoftheday",
            iam_roles=[role.role_arn],
            tags=[self.tag_system]
        )

        cfn_workgroup = redshiftserverless.CfnWorkgroup(self, "Workgroup",
            workgroup_name="newsoftheday-workgroup",
            namespace_name=cfn_namespace.namespace_name,
            tags=[self.tag_system]
        )

        cfn_workgroup.node.add_dependency(cfn_namespace)
