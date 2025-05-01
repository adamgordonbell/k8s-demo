import pulumi
import pulumi_kubernetes as k8s
from pulumi_kubernetes.apps.v1 import Deployment, DeploymentSpecArgs
from pulumi_kubernetes.core.v1 import Service, ServiceSpecArgs, PodTemplateSpecArgs, PodSpecArgs, ContainerArgs, ContainerPortArgs, ServicePortArgs
from pulumi_kubernetes.meta.v1 import ObjectMetaArgs, LabelSelectorArgs
from pulumi.resource import ResourceOptions

from pulumi_aws import s3
import pulumi_kubernetes as k8s

config = pulumi.Config()
org = config.require("org")
stack = pulumi.get_stack()

# Reference the EKS cluster stack to get kubeconfig
eks_stack = pulumi.StackReference(f"{org}/KubeKitties/{stack}")
kubeconfig = eks_stack.get_output("kubeconfig")


# Create Kubernetes provider
k8s_provider = k8s.Provider('k8s-provider',
    kubeconfig=kubeconfig
)

# Define labels for our app
app_labels = { "app": "cat-app" }

# Create a Deployment using your Docker image
cat_deployment = Deployment(
    "cat-deployment",
    metadata=ObjectMetaArgs(
        labels=app_labels,
    ),
    spec=DeploymentSpecArgs(
        replicas=2,
        selector=LabelSelectorArgs(
            match_labels=app_labels,
        ),
        template=PodTemplateSpecArgs(
            metadata=ObjectMetaArgs(labels=app_labels),
            spec=PodSpecArgs(
                containers=[
                    ContainerArgs(
                        name="cat-server",
                        image="agbell/my-random-cat",
                        ports=[ContainerPortArgs(container_port=8080)],
                    ),
                ],
            ),
        ),
    ),
    opts=ResourceOptions(provider=k8s_provider),
)

# Create a LoadBalancer Service that maps port 80 to 8080
cat_service =Service(
    "cat-service",
    metadata=ObjectMetaArgs(labels=app_labels),
    spec=ServiceSpecArgs(
        type="LoadBalancer",
        selector=app_labels,
        ports=[ServicePortArgs(port=80, target_port=8080)],
    ),
    opts=ResourceOptions(provider=k8s_provider),
)

pulumi.export("kubeconfig",kubeconfig)
pulumi.export("catServiceUrl", cat_service.status.load_balancer.ingress[0].hostname)