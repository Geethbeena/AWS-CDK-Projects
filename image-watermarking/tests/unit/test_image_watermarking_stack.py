import aws_cdk as core
import aws_cdk.assertions as assertions

from image_watermarking.image_watermarking_stack import ImageWatermarkingStack

# example tests. To run these tests, uncomment this file along with the example
# resource in image_watermarking/image_watermarking_stack.py
def test_sqs_queue_created():
    app = core.App()
    stack = ImageWatermarkingStack(app, "image-watermarking")
    template = assertions.Template.from_stack(stack)

#     template.has_resource_properties("AWS::SQS::Queue", {
#         "VisibilityTimeout": 300
#     })
