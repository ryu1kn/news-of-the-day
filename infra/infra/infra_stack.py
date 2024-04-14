import os

from aws_cdk import (
    Stack,
    aws_glue,
    aws_iam,
    aws_redshiftserverless as redshiftserverless,
    aws_s3,
    RemovalPolicy,
)
from constructs import Construct


class InfraStack(Stack):

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

        cfn_namespace = redshiftserverless.CfnNamespace(self, "Namespace",
            namespace_name="newsoftheday-namespace",

            # Temporary settings for spiking
            admin_username=os.environ['REDSHIFT_ADMIN_USERNAME'],
            admin_user_password=os.environ['REDSHIFT_ADMIN_USER_PASSWORD'],

            db_name="newsoftheday",
            iam_roles=[role.role_arn]
        )

        cfn_workgroup = redshiftserverless.CfnWorkgroup(self, "Workgroup",
            workgroup_name="newsoftheday-workgroup",
            namespace_name=cfn_namespace.namespace_name,
        )
        cfn_workgroup.node.add_dependency(cfn_namespace)

        news_bucket = aws_s3.Bucket(self, "NewsBucket",
            bucket_name="newsoftheday-news",
            removal_policy=RemovalPolicy.DESTROY
        )

        cfn_glue_database = aws_glue.CfnDatabase(self, "GlueDatabase",
            catalog_id=self.account,
            database_input=aws_glue.CfnDatabase.DatabaseInputProperty(name="newsoftheday-news")
        )

        glue_role = aws_iam.Role(
            self,
            "GlueRole",
            role_name="newsoftheday-glue-role",

            assumed_by=aws_iam.CompositePrincipal(
                aws_iam.ServicePrincipal("glue.amazonaws.com")
            ),
            managed_policies=[aws_iam.ManagedPolicy.from_aws_managed_policy_name("service-role/AWSGlueServiceRole")],
            inline_policies={
                "S3BucketAccessPolicy": aws_iam.PolicyDocument(
                    statements=[
                        aws_iam.PolicyStatement(
                            actions=["s3:GetObject", "s3:PutObject"],
                            effect=aws_iam.Effect.ALLOW,
                            resources=[news_bucket.arn_for_objects("digests/*")]
                        )
                    ]
                )
            }
        )

        aws_glue.CfnCrawler(self, "GlueTable",
            name="newsoftheday-news-digests-crawler",
            role=glue_role.role_arn,
            database_name=cfn_glue_database.database_input.name,
            targets=aws_glue.CfnCrawler.TargetsProperty(
                s3_targets=[aws_glue.CfnCrawler.S3TargetProperty(
                    path=news_bucket.s3_url_for_object("digests")
                )]
            )
        )

