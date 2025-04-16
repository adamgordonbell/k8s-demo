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

# Define labels for our app
app_labels = { "app": "cat-app" }

# Create a Deployment using your Docker image
cat_deployment = k8s.apps.v1.Deployment(
    "cat-deployment",
    spec={
        "selector": {"matchLabels": app_labels},
        "replicas": 2,
        "template": {
            "metadata": {"labels": app_labels},
            "spec": {
                "containers": [{
                    "name": "cat-server",
                    "image": "agbell/my-random-cat",
                    "ports": [{"containerPort": 8080}],
                }]
            }
        }
    },
    opts=pulumi.ResourceOptions(provider=k8s_provider)
)

# Create a LoadBalancer Service that maps port 80 to 8080
cat_service = k8s.core.v1.Service(
    "cat-service",
    metadata={
        "labels": app_labels,
    },
    spec={
        "type": "LoadBalancer",
        "selector": app_labels,
        "ports": [{
            "port": 80,
            "targetPort": 8080
        }]
    },
    opts=pulumi.ResourceOptions(provider=k8s_provider)
)

pulumi.export("kubeconfig", eks_cluster.kubeconfig)
pulumi.export("vpc_id",eks_vpc.vpc_id)
pulumi.export("catServiceUrl", cat_service.status.load_balancer.ingress[0].hostname)