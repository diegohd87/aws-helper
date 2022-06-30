#!/usr/bin/env python
import boto3
import argparse

# script to find unused security groups
# https://aws.amazon.com/premiumsupport/knowledge-center/ec2-find-security-group-resources/

def lookup_by_id(sgid):
    sg = ec2.get_all_security_groups(group_ids=sgid)
    return sg[0].name

# get region list
client = boto3.client("ec2")
regions_dictionary = client.describe_regions()
region_list = [region["RegionName"] for region in regions_dictionary["Regions"]]

# It allows to use arguments. In this case, allows to use region as an argument.
# The default region is us-east-2
parser = argparse.ArgumentParser(description="Unused security groups")
parser.add_argument("-r", "--region", type=str, default="us-east-2",
                    help="The default region is us-east-2. The list of available regions: %s" % sorted(
                        region_list))
args = parser.parse_args()

# get ec2 resources by region
client = boto3.client("ec2", region_name=args.region)
ec2 = boto3.resource("ec2", region_name=args.region)
all_groups = []
security_groups_in_use = []

# get security groups names
# https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/ec2.html#EC2.Client.describe_security_groups
sg = client.describe_security_groups()
security_groups = sg["SecurityGroups"]
for groupobj in security_groups:
    if groupobj["GroupName"] == "default" or groupobj["GroupName"].startswith("d-"):
        security_groups_in_use.append(groupobj["GroupId"])
    all_groups.append(groupobj["GroupId"])

# Get all security groups used by instances
# https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/ec2.html#EC2.Client.describe_instances
instances = client.describe_instances()
reservations = instances["Reservations"]
network_interface_count = 0

for i in reservations:
    for j in i["Instances"]:
        for k in j["SecurityGroups"]:
            if k["GroupId"] not in security_groups_in_use:
                security_groups_in_use.append(k["GroupId"])		

# Security Groups in use by Network Interfaces
# https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/ec2.html#EC2.Client.describe_network_interfaces				
eni_client = boto3.client("ec2", region_name=args.region)
eni = eni_client.describe_network_interfaces()
for i in eni["NetworkInterfaces"]:
	for j in i["Groups"]:
		if j["GroupId"] not in security_groups_in_use:
			security_groups_in_use.append(j["GroupId"])

# Security groups used by classic ELBs
# https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/elb.html#ElasticLoadBalancing.Client.describe_load_balancers
elb_client = boto3.client("elb", region_name=args.region)
elb = elb_client.describe_load_balancers()
for i in elb["LoadBalancerDescriptions"]:
    for j in i["SecurityGroups"]:
        if j not in security_groups_in_use:
            security_groups_in_use.append(j)

# Security groups used by ALBs
# https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/elbv2.html#ElasticLoadBalancingv2.Client.describe_load_balancers
elb2_client = boto3.client("elbv2", region_name=args.region)
elb2 = elb2_client.describe_load_balancers()
for i in elb2["LoadBalancers"]:
    if "SecurityGroups" in i:
        for j in i["SecurityGroups"]:
            if j not in security_groups_in_use:
                        security_groups_in_use.append(j)
    else:
        print(f"ALB -> {i['LoadBalancerName']} didn't use any security group")

# Security groups used by RDS
# https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/rds.html?highlight=describe_db_instances#RDS.Client.describe_db_instances
rds_client = boto3.client("rds", region_name=args.region)
rds = rds_client.describe_db_instances()
for i in rds["DBInstances"]:
	for j in i["VpcSecurityGroups"]:
		if j["VpcSecurityGroupId"] not in security_groups_in_use:
			security_groups_in_use.append(j["VpcSecurityGroupId"])

delete_candidates = []
for group in all_groups:
    if group not in security_groups_in_use:
        delete_candidates.append(group)

print("Report")

print("Total number of Security Groups:{0:d}".format(len(all_groups)))
print(u"Total number of EC2 Instances: {0:d}".format(len(reservations)))
print(u"Total number of Load Balancers: {0:d}".format(len(elb["LoadBalancerDescriptions"]) +
                                                                len(elb2["LoadBalancers"])))
print(u"Total number of RDS Instances: {0:d}".format(len(rds["DBInstances"])))
print(u"Total number of Network Interfaces: {0:d}".format(len(eni["NetworkInterfaces"])))
print(u"Total number of Security Groups in-use: {0:d}".format(len(security_groups_in_use)))
print(u"Total number of Unused Security Groups targeted for removal: {0:d}".format(len(delete_candidates)))
print(delete_candidates)