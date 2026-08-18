{
  "AWSTemplateFormatVersion": "2010-09-09",
  "Description": "Gladiator VPC with public/private subnets, Internet Gateway, route tables, security group, key pair, and an Apache-hosted EC2 instance (eClerxServer01) in ap-south-1.",

  "Resources": {

    "GladiatorVPC": {
      "Type": "AWS::EC2::VPC",
      "Properties": {
        "CidrBlock": "10.10.0.0/16",
        "EnableDnsSupport": true,
        "EnableDnsHostnames": true,
        "Tags": [
          { "Key": "Name", "Value": "Gladiator" }
        ]
      }
    },

    "GladiatorIGW": {
      "Type": "AWS::EC2::InternetGateway",
      "Properties": {
        "Tags": [
          { "Key": "Name", "Value": "Gladiator-IGW" }
        ]
      }
    },

    "IGWAttachment": {
      "Type": "AWS::EC2::VPCGatewayAttachment",
      "Properties": {
        "VpcId": { "Ref": "GladiatorVPC" },
        "InternetGatewayId": { "Ref": "GladiatorIGW" }
      }
    },

    "PublicSubnet1": {
      "Type": "AWS::EC2::Subnet",
      "Properties": {
        "VpcId": { "Ref": "GladiatorVPC" },
        "CidrBlock": "10.10.10.0/24",
        "AvailabilityZone": "ap-south-1a",
        "MapPublicIpOnLaunch": true,
        "Tags": [
          { "Key": "Name", "Value": "Gladiator-Public-Subnet-1" }
        ]
      }
    },

    "PrivateSubnet1": {
      "Type": "AWS::EC2::Subnet",
      "Properties": {
        "VpcId": { "Ref": "GladiatorVPC" },
        "CidrBlock": "10.10.20.0/24",
        "AvailabilityZone": "ap-south-1b",
        "MapPublicIpOnLaunch": false,
        "Tags": [
          { "Key": "Name", "Value": "Gladiator-Private-Subnet-1" }
        ]
      }
    },

    "PublicRouteTable": {
      "Type": "AWS::EC2::RouteTable",
      "Properties": {
        "VpcId": { "Ref": "GladiatorVPC" },
        "Tags": [
          { "Key": "Name", "Value": "Gladiator-Public-RT" }
        ]
      }
    },

    "PublicInternetRoute": {
      "Type": "AWS::EC2::Route",
      "DependsOn": "IGWAttachment",
      "Properties": {
        "RouteTableId": { "Ref": "PublicRouteTable" },
        "DestinationCidrBlock": "0.0.0.0/0",
        "GatewayId": { "Ref": "GladiatorIGW" }
      }
    },

    "PublicSubnet1RouteTableAssociation": {
      "Type": "AWS::EC2::SubnetRouteTableAssociation",
      "Properties": {
        "SubnetId": { "Ref": "PublicSubnet1" },
        "RouteTableId": { "Ref": "PublicRouteTable" }
      }
    },

    "PrivateRouteTable": {
      "Type": "AWS::EC2::RouteTable",
      "Properties": {
        "VpcId": { "Ref": "GladiatorVPC" },
        "Tags": [
          { "Key": "Name", "Value": "Gladiator-Private-RT" }
        ]
      }
    },

    "PrivateSubnet1RouteTableAssociation": {
      "Type": "AWS::EC2::SubnetRouteTableAssociation",
      "Properties": {
        "SubnetId": { "Ref": "PrivateSubnet1" },
        "RouteTableId": { "Ref": "PrivateRouteTable" }
      }
    },

    "GladSecGrp1": {
      "Type": "AWS::EC2::SecurityGroup",
      "Properties": {
        "GroupName": "GladSecGrp1",
        "GroupDescription": "Allow SSH and HTTP from anywhere",
        "VpcId": { "Ref": "GladiatorVPC" },
        "SecurityGroupIngress": [
          {
            "IpProtocol": "tcp",
            "FromPort": 22,
            "ToPort": 22,
            "CidrIp": "0.0.0.0/0",
            "Description": "Allow SSH"
          },
          {
            "IpProtocol": "tcp",
            "FromPort": 80,
            "ToPort": 80,
            "CidrIp": "0.0.0.0/0",
            "Description": "Allow HTTP"
          }
        ],
        "SecurityGroupEgress": [
          {
            "IpProtocol": "-1",
            "CidrIp": "0.0.0.0/0",
            "Description": "Allow all outbound traffic"
          }
        ],
        "Tags": [
          { "Key": "Name", "Value": "GladSecGrp1" }
        ]
      }
    },

    "GladInstanceKey1": {
      "Type": "AWS::EC2::KeyPair",
      "Properties": {
        "KeyName": "GladInstanceKey1",
        "KeyType": "rsa",
        "KeyFormat": "pem",
        "Tags": [
          { "Key": "Name", "Value": "GladInstanceKey1" }
        ]
      }
    },

    "eClerxServer01": {
      "Type": "AWS::EC2::Instance",
      "DependsOn": "PublicSubnet1RouteTableAssociation",
      "Properties": {
        "ImageId": "ami-00d2dbb426772b03a",
        "InstanceType": "t3.micro",
        "KeyName": { "Ref": "GladInstanceKey1" },
        "SubnetId": { "Ref": "PublicSubnet1" },
        "SecurityGroupIds": [ { "Ref": "GladSecGrp1" } ],
        "BlockDeviceMappings": [
          {
            "DeviceName": "/dev/xvda",
            "Ebs": {
              "VolumeSize": 8,
              "VolumeType": "gp3",
              "DeleteOnTermination": true
            }
          }
        ],
        "Tags": [
          { "Key": "Name", "Value": "eClerxServer01" }
        ],
        "UserData": {
          "Fn::Base64": {
            "Fn::Join": [
              "\n",
              [
                "#!/bin/bash",
                "# Update the system",
                "sudo yum update -y",
                "# Install Apache web server",
                "sudo yum install -y httpd",
                "# Start Apache",
                "sudo systemctl start httpd",
                "# Enable Apache to start on system boot",
                "sudo systemctl enable httpd",
                "# Create the index.html file",
                "sudo bash -c 'cat > /var/www/html/index.html <<EOF",
                "<!DOCTYPE html>",
                "<html>",
                "<head>",
                "<style>",
                "body {",
                "    background-color: lightgreen;",
                "}",
                "h1 {",
                "    font-size: 48px;",
                "    font-weight: bold;",
                "}",
                "</style>",
                "</head>",
                "<body>",
                "<h1>AWS Training: CloudFormation  2026</h1>",
                "</body>",
                "</html>",
                "EOF'",
                "# Set ownership and permissions for the index.html file",
                "sudo chown apache:apache /var/www/html/index.html",
                "sudo chmod 644 /var/www/html/index.html",
                "# Restart Apache to apply the changes",
                "sudo systemctl restart httpd"
              ]
            ]
          }
        }
      }
    }
  },

  "Outputs": {
    "VPCId": {
      "Description": "VPC ID of Gladiator VPC",
      "Value": { "Ref": "GladiatorVPC" }
    },
    "PublicSubnetId": {
      "Description": "Public Subnet ID (ap-south-1a)",
      "Value": { "Ref": "PublicSubnet1" }
    },
    "PrivateSubnetId": {
      "Description": "Private Subnet ID (ap-south-1b)",
      "Value": { "Ref": "PrivateSubnet1" }
    },
    "SecurityGroupId": {
      "Description": "Security Group ID for GladSecGrp1",
      "Value": { "Ref": "GladSecGrp1" }
    },
    "InstanceId": {
      "Description": "Instance ID of eClerxServer01",
      "Value": { "Ref": "eClerxServer01" }
    },
    "InstancePublicIP": {
      "Description": "Public IP address of eClerxServer01",
      "Value": { "Fn::GetAtt": [ "eClerxServer01", "PublicIp" ] }
    },
    "WebsiteURL": {
      "Description": "URL to test the Apache web server",
      "Value": {
        "Fn::Join": [
          "",
          [ "http://", { "Fn::GetAtt": [ "eClerxServer01", "PublicIp" ] } ]
        ]
      }
    },
    "KeyPairRetrieval": {
      "Description": "How to retrieve the PEM private key created by CloudFormation",
      "Value": "aws ssm get-parameter --name /ec2/keypair/{KeyPairId} --with-decryption --query Parameter.Value --output text --region ap-south-1 > GladInstanceKey1.pem"
    }
  }
}
