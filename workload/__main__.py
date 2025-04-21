"""An AWS Python Pulumi program"""

import pulumi
from pulumi_aws import s3
import pulumi_kubernetes as k8s

config = pulumi.Config()
org = config.require("org")
stack = pulumi.get_stack()

# Reference the EKS cluster stack to get kubeconfig
eks_stack = pulumi.StackReference(f"{org}/KubeKitties/{stack}")
kubeconfig = eks_stack.get_output("kubeconfig")

# Create Kubernetes provider using the kubeconfig
k8s_provider = k8s.Provider("k8s-provider", kubeconfig=kubeconfig)

# Deploy resources from YAML files
cat_deployment_yaml = k8s.yaml.ConfigFile("cat-deployment",
    file="yaml/cat-deployment.yaml",
    opts=pulumi.ResourceOptions(provider=k8s_provider)
)

cat_service_yaml = k8s.yaml.ConfigFile("cat-service",
    file="yaml/cat-service.yaml",
    opts=pulumi.ResourceOptions(provider=k8s_provider)
)

# Export the service URL
pulumi.export("catServiceUrl", cat_service_yaml.get_resource("v1/Service", "cat-service").status.load_balancer.ingress[0].hostname)