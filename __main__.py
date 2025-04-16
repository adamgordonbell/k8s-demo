import pulumi
import pulumi_awsx as awsx
import pulumi_eks as eks
import pulumi_kubernetes as k8s

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

pulumi.export("kubeconfig", eks_cluster.kubeconfig)
pulumi.export("vpc_id",eks_vpc.vpc_id)
# pulumi.export("url", pulumi.Output.concat("http://", service.status.load_balancer.ingress[0].hostname))