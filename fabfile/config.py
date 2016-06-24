import os.path

# Zones

QUUUX_STACK = {
    "AWSTemplateFormatVersion": "2010-09-09",
    "Description": "Zone configurations",

    "Resources": {
        "Zone": {
            "Type": "AWS::Route53::HostedZone",
            "Properties": {
                "Name": "quuux.org"
            }
        },
    },
}


# Website config

STATIC_WEBSITES = [
    # (path, bucket)
    (os.path.expanduser("~/Web/marcdellavolpe.com"), "marcdellavolpe.com"),
]

WEBSITE_STACK = {
    "AWSTemplateFormatVersion": "2010-09-09",
    "Description": "Website configurations",

    "Resources": {

        "ZoneMarcDellaVolpe": {
            "Type": "AWS::Route53::HostedZone",
            "Properties": {
                "Name": "marcdellavolpe.com"
            }
        },

        "BucketMarcDellaVolpeCom": {
            "Type": "AWS::S3::Bucket",
            "Properties": {
                "BucketName": "marcdellavolpe.com",
                "AccessControl": "PublicRead",
                "WebsiteConfiguration": {
                    "IndexDocument": "index.html"
                }
            }
        },

        "Hosts": {
            "Type": "AWS::Route53::RecordSetGroup",
            "DependsOn": "ZoneMarcDellaVolpe",
            "Properties": {
                "HostedZoneName": "marcdellavolpe.com.",
                "RecordSets": [{
                    "Name": "marcdellavolpe.com.",
                    "Type": "A",
                    "AliasTarget": {
                        "HostedZoneId": "Z3AQBSTGFYJSTF",
                        "DNSName": "s3-website-us-east-1.amazonaws.com"
                    }},
                    {
                        "Name": "marcdellavolpe.com.",
                        "Type": "MX",
                        "TTL": "60",
                        "ResourceRecords": [
                            "10 snake.quuux.org.",
                        ]
                    }
                ]
            },
        },
    }
}

# Shell config

USER = 'marc'
SHELL_HOSTNAME = 'snake.quuux.org'
SHELL_SIZE = "t2.nano"
SHELL_AMI = "ami-f652979b"

SHELL_STACK = {
    "AWSTemplateFormatVersion": "2010-09-09",
    "Description": "Shell",

    "Outputs": {
        "AZ": {
            "Description": "Availability Zone of the newly created EC2 instance",
            "Value": {"Fn::GetAtt": ["Shell", "AvailabilityZone"]}
        },
        "InstanceId": {
            "Description": "InstanceId of the newly created EC2 instance",
            "Value": {"Ref": "Shell"}
        },
        "PublicDNS": {
            "Description": "Public DNSName of the newly created EC2 instance",
            "Value": {"Fn::GetAtt": ["Shell", "PublicDnsName"]}
        },
        "PublicIP": {
            "Description": "Public IP address of the newly created EC2 instance",
            "Value": {"Fn::GetAtt": ["Shell", "PublicIp"]}
        }
    },
    "Resources": {

        "Shell": {
            "Type": "AWS::EC2::Instance",
            "Properties": {
                "ImageId": SHELL_AMI,
                "InstanceType": SHELL_SIZE,
                "KeyName": "marc",
                "NetworkInterfaces": [
                    {
                        "AssociatePublicIpAddress": "true",
                        "DeleteOnTermination": "true",
                        "DeviceIndex": "0",
                        "GroupSet": [{"Ref": "InstanceSecurityGroup"}],
                        "SubnetId": {"Ref": "Subnet"}
                    }
                ],
                "Tags": [
                    {"Key": "Name", "Value": "Shell"},
                ]
            },
        },

        "Hosts": {
            "Type": "AWS::Route53::RecordSetGroup",
            "Properties": {
                "HostedZoneName": "quuux.org.",
                "RecordSets": [
                    {
                        "Name": "snake.quuux.org.",
                        "Type": "A",
                        "TTL": "60",
                        "ResourceRecords": [{"Ref": "IPAddress"}]
                    },
                    {
                        "Name": "quuux.org.",
                        "Type": "MX",
                        "TTL": "60",
                        "ResourceRecords": [
                            "10 snake.quuux.org.",
                        ]
                    }
                ]
            },
        },

        "AttachGateway": {
            "Type": "AWS::EC2::VPCGatewayAttachment",
            "Properties": {
                "InternetGatewayId": {"Ref": "InternetGateway"},
                "VpcId": {"Ref": "VPC"}
            }
        },
        "IPAddress": {
            "Type": "AWS::EC2::EIP",
            "DependsOn": "AttachGateway",
            "Properties": {
                "Domain": "vpc",
                "InstanceId": {"Ref": "Shell"}
            },
        },
        "InboundSSHNetworkAclEntry": {
            "Type": "AWS::EC2::NetworkAclEntry",
            "Properties": {
                "CidrBlock": "0.0.0.0/0",
                "Egress": "false",
                "NetworkAclId": {"Ref": "NetworkAcl"},
                "PortRange": {
                    "From": "22",
                    "To": "22"
                },
                "Protocol": "6",
                "RuleAction": "allow",
                "RuleNumber": "101"
            }
        },
        "InboundSMTPNetworkAclEntry": {
            "Type": "AWS::EC2::NetworkAclEntry",
            "Properties": {
                "CidrBlock": "0.0.0.0/0",
                "Egress": "false",
                "NetworkAclId": {"Ref": "NetworkAcl"},
                "PortRange": {
                    "From": "25",
                    "To": "25"
                },
                "Protocol": "6",
                "RuleAction": "allow",
                "RuleNumber": "102"
            }
        },
        "InstanceSecurityGroup": {
            "Type": "AWS::EC2::SecurityGroup",
            "Properties": {
                "GroupDescription": "Enable SSH access via port 22",
                "SecurityGroupIngress": [
                    {
                        "CidrIp": "0.0.0.0/0",
                        "FromPort": "22",
                        "IpProtocol": "tcp",
                        "ToPort": "22"
                    },
                    {
                        "CidrIp": "0.0.0.0/0",
                        "FromPort": "25",
                        "IpProtocol": "tcp",
                        "ToPort": "25"
                    }
                ],
                "VpcId": {"Ref": "VPC"}
            },
        },
        "InternetGateway": {
            "Properties": {},
            "Type": "AWS::EC2::InternetGateway"
        },
        "NetworkAcl": {
            "Properties": {"VpcId": {"Ref": "VPC"}},
            "Type": "AWS::EC2::NetworkAcl"
        },
        "Route": {
            "Type": "AWS::EC2::Route",
            "DependsOn": "AttachGateway",
            "Properties": {
                "DestinationCidrBlock": "0.0.0.0/0",
                "GatewayId": {"Ref": "InternetGateway"},
                "RouteTableId": {"Ref": "RouteTable"}
            },
        },
        "RouteTable": {
            "Properties": {
                "VpcId": {"Ref": "VPC"}
            },
            "Type": "AWS::EC2::RouteTable"
        },
        "Subnet": {
            "Type": "AWS::EC2::Subnet",
            "Properties": {
                "CidrBlock": "10.0.0.0/24",
                "VpcId": {"Ref": "VPC"}
            },
        },
        "SubnetRouteTableAssociation": {
            "Type": "AWS::EC2::SubnetRouteTableAssociation",
            "Properties": {
                "RouteTableId": {"Ref": "RouteTable"},
                "SubnetId": {"Ref": "Subnet"}
            },
        },
        "VPC": {
            "Type": "AWS::EC2::VPC",
            "Properties": {
                "CidrBlock": "10.0.0.0/16",
                "EnableDnsHostnames": "true",
                "EnableDnsSupport": "true"
            },
        }
    }
}

BASE_PACKAGES = [
    "curl",
    "python-software-properties",
    "emacs-nox",
    "build-essential",
    "python-pip",
    "python-setuptools",
    "python-dev",
    "tmux",
    "git",
    "irssi",
    "irssi-scripts",
]

MAIL_FORWARDS = [
    "quuux.org",
    "marcdellavolpe.com"
]

FORWARD_TO = "marc.dellavolpe+{domain}@gmail.com"
