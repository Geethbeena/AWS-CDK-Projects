from aws_cdk import (
    # Duration,
    core,
    Stack,
    aws_s3 as s3,
    aws_lambda as _lambda,
    aws_s3objectlambda as s3objectlambda
)
from constructs import Construct
import os, subprocess

class ImageWatermarkingStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # The code that defines your stack goes here

        bucket = s3.Bucket(self, 
            "MyImageBucket",
            versioned=True,
            removal_policy=core.RemovalPolicy.DESTROY
        )

        access_point = s3.CfnAccessPoint(self, "MyImageBucketAccessPoint",
                                         bucket = bucket.bucket_name,
                                         name="my-access-point")
    
        
        my_lambda = _lambda.Function(
            self,
            id="MyLambda",
            runtime=_lambda.Runtime.PYTHON_3_10,
            handler="index.handler",
            code=_lambda.Code.from_asset("lambda"),
            layers=[self.create_dependencies_layer(self.stack_name, "lambda/index")],
        )

        content_transformation_property = s3objectlambda.CfnAccessPoint.ContentTransformationProperty(
            aws_lambda=s3objectlambda.CfnAccessPoint.AwsLambdaProperty(
                function_arn=my_lambda.function_arn
            )
        )

        cfn_access_point = s3objectlambda.CfnAccessPoint(self, "MyCfnAccessPoint",
            object_lambda_configuration=s3objectlambda.CfnAccessPoint.ObjectLambdaConfigurationProperty(
                supporting_access_point=access_point.name,
                transformation_configurations=[s3objectlambda.CfnAccessPoint.TransformationConfigurationProperty(
                    actions=["GetObject"],
                    content_transformation=content_transformation_property
                )],

                # the properties below are optional
                allowed_features=["allowedFeatures"],
                cloud_watch_metrics_enabled=False
            ),

        )
    
    def create_dependencies_layer(self, project_name, function_name: str) -> _lambda.LayerVersion:
        requirements_file = "lambda/requirements.txt"  # 👈🏽 point to requirements.txt
        output_dir = f".build/app"  # 👈🏽 a temporary directory to store the dependencies

        if not os.environ.get("SKIP_PIP"):
            # 👇🏽 download the dependencies and store them in the output_dir
            subprocess.check_call(f"pip install -r {requirements_file} -t {output_dir}/python".split())

        layer_id = f"{project_name}-{function_name}-dependencies"  # 👈🏽 a unique id for the layer
        layer_code = _lambda.Code.from_asset(output_dir)  # 👈🏽 import the dependencies / code

        my_layer = _lambda.LayerVersion(
            self,
            layer_id,
            code=layer_code,
        )

        return my_layer
