# Full Documentation for S3
# https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/ec2.html?highlight=describe_security_groups#EC2.Client.describe_security_groups
from logging import exception
import boto3

# Security Groups
ec2 = boto3.client('ec2',region_name='us-east-2')
sg = ec2.describe_security_groups()

for i in sg["SecurityGroups"]:
   print ("------------------------------------------------") 
   print ("Security Group Id: "+i["GroupId"]+' - Name: '+i["GroupName"] + " VPCId: " +i["VpcId"])
    
   print ("IP PERMISSIONS")
   for j in i["IpPermissions"]:
       print ("IP Protocol: "+j["IpProtocol"])
       try:
          print ("FROM PORT: "+str(j["FromPort"]))
          for k in j["IpRanges"]:
              print ("IP Ranges: "+k["CidrIp"])
       except Exception:
          print ("No value for FromPort and ip ranges available for this security group")
          continue
       try:
          print ("Ipv6Ranges")
          for k in j["Ipv6Ranges"]:
              print ("IP v6 Ranges: "+k["CidrIpv6"])
       except Exception:
          print ("No value for Ipv6 ranges available for this security group")
          continue
       try:
           print ("TO PORT: "+str(j["ToPort"]))
       except Exception:
          print ("No value for ToPort and ip ranges available for this security group")
          continue

   print ("IP PERMISSION EGRESS")
   for j in i["IpPermissionsEgress"]:
       print ("IP Protocol: "+j['IpProtocol'])
       try:
          print ("FromPort: "+str(j["FromPort"]))
          for k in j["IpRanges"]:
              print ("IP Ranges: "+k["CidrIp"])
       except Exception:
          print ("No value for FromPort and ip ranges available for this security group")
          continue
       try:
          print ("Ipv6Ranges")
          for k in j["Ipv6Ranges"]:
              print ("IP v6 Ranges: "+k["CidrIpv6"])
       except Exception:
          print ("No value for Ipv6 ranges available for this security group")
          continue
       try:
           print ("TO PORT: "+str(j["ToPort"]))
       except Exception:
          print ("No value for ToPort and ip ranges available for this security group")
          continue
