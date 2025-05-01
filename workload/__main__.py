import pulumi

from pulumi_aws import s3
import pulumi_kubernetes as k8s

config = pulumi.Config()
org = config.require("org")
stack = pulumi.get_stack()

# Reference the EKS cluster stack to get kubeconfig
eks_stack = pulumi.StackReference(f"{org}/KubeKitties/{stack}")
kubeconfig = eks_stack.get_output("kubeconfig")