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


# Create VPC with default CIDR
eks_vpc = awsx.ec2.Vpc("eks-vpc",
    enable_dns_hostnames=True)

# Create minimal EKS cluster with EC2 nodes
eks_cluster = eks.Cluster("eks-cluster",
    vpc_id=eks_vpc.vpc_id,
    private_subnet_ids=eks_vpc.private_subnet_ids,
    skip_default_node_group=False,
    instance_type="t3.micro",
    desired_capacity=2,
    min_size=1,
    max_size=3,
)

# Create Kubernetes provider
k8s_provider = k8s.Provider('k8s-provider',
    kubeconfig=eks_cluster.kubeconfig
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
cat_service = core_v1.Service(
    "cat-service",
    metadata=meta_v1.ObjectMetaArgs(labels=app_labels),
    spec=core_v1.ServiceSpecArgs(
        type="LoadBalancer",
        selector=app_labels,
        ports=[core_v1.ServicePortArgs(port=80, target_port=8080)],
    ),
    opts=ResourceOptions(provider=k8s_provider),
)

pulumi.export("kubeconfig", eks_cluster.kubeconfig)
pulumi.export("vpc_id",eks_vpc.vpc_id)
pulumi.export("catServiceUrl", cat_service.status.load_balancer.ingress[0].hostname)