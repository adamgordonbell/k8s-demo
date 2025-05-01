import pulumi

config = pulumi.Config()
pulumi_tags = config.require("pulumi:tags")
