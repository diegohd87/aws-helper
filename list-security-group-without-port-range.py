from logging import exception
import boto3
import argparse

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

# Security Groups
client = boto3.client("ec2", region_name=args.region)
security_groups_not_range = []

# get security without port range
# https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/ec2.html#EC2.Client.describe_security_groups
sg = client.describe_security_groups()
security_groups = sg["SecurityGroups"]
for groupobj in security_groups:
    for port_range in groupobj["IpPermissions"]:
        try:
            str(port_range["FromPort"])
        except Exception:
            security_groups_not_range.append(groupobj["GroupId"] + " - " + groupobj["GroupName"] +" - " + groupobj["Description"])

print(security_groups_not_range)
