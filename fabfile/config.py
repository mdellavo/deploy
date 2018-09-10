import os.path

CONFIGS_PATH = os.path.join(os.path.dirname(__file__), "..", "config")

DOMAIN = "quuux.org"
KNAPSACK_WEB_HOST = "knapsack." + DOMAIN
GDAX_TRADER_HOST = "gdax-trader." + DOMAIN
SELF_HOST = "marcdellavolpe.com"

SHELL_HOST = MX = "snake.quuux.org"

WEBSITE_STACK = {
    "AWSTemplateFormatVersion": "2010-09-09",
    "Description": "Website configurations",

    "Resources": {

        "ZoneMarcDellaVolpe": {
            "Type": "AWS::Route53::HostedZone",
            "Properties": {
                "Name": SELF_HOST
            }
        },

        "BucketMarcDellaVolpeCom": {
            "Type": "AWS::S3::Bucket",
            "Properties": {
                "BucketName": SELF_HOST,
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
                "HostedZoneName": SELF_HOST + ".",
                "RecordSets": [
                    {
                        "Name": SELF_HOST + ".",
                        "Type": "A",
                        "AliasTarget": {
                            "HostedZoneId": "Z3AQBSTGFYJSTF",
                            "DNSName": "s3-website-us-east-1.amazonaws.com"
                        }
                    },
                    {
                        "Name": SELF_HOST + ".",
                        "Type": "MX",
                        "TTL": "60",
                        "ResourceRecords": [
                            "10 {}.".format(MX),
                        ]
                    },
                    {
                        "Name": SELF_HOST,
                        "Type": "TXT",
                        "TTL": "60",
                        "ResourceRecords": [
                            "\"google-site-verification=KasvFeWlCVAUYQ2xIU8ZabVi8SVbxwOieWQVEV6uF70\"",
                            "\"v=spf1 mx -all\"",
                        ]
                    },
                ]
            },
        },
    }
}

# Shell config

AZ = "us-east-1b"
SHELL_SIZE = "t2.small"
SHELL_AMI = "ami-45b69e52"

HOMES_SIZE = "25"  # GB
HOMES_DEVICE_EXT = "h"
HOMES_DEVICE = "/dev/xvd" + HOMES_DEVICE_EXT

DB_SIZE = "5"  # GB
DB_DEVICE_EXT = "i"
DB_DEVICE = "/dev/xvd" + DB_DEVICE_EXT

DB_PATH = "/db"


SHELL_STACK = {
    "AWSTemplateFormatVersion": "2010-09-09",
    "Description": "Shell",

    "Outputs": {
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
                "Volumes": [
                    {
                        "VolumeId": {"Ref": "HomeVolume"},
                        "Device": "/dev/sd" + HOMES_DEVICE_EXT
                    },
                    {
                        "VolumeId": {"Ref": "DBVolume"},
                        "Device": "/dev/sd" + DB_DEVICE_EXT
                    },
                ],
                "Tags": [
                    {"Key": "Name", "Value": "Shell"},
                ]
            },
        },

        "HomeVolume": {
            "Type": "AWS::EC2::Volume",
            "Properties": {
                "Size": HOMES_SIZE,
                "Encrypted": "true",
                "AvailabilityZone": AZ,
            }
        },

        "DBVolume": {
            "Type": "AWS::EC2::Volume",
            "Properties": {
                "Size": DB_SIZE,
                "Encrypted": "true",
                "AvailabilityZone": AZ,
            }
        },

        "BucketKnapsackWeb": {
            "Type": "AWS::S3::Bucket",
            "Properties": {
                "BucketName": KNAPSACK_WEB_HOST,
                "AccessControl": "PublicRead",
                "WebsiteConfiguration": {
                    "IndexDocument": "index.html"
                }
            }
        },

        "BucketGDAXTraderWeb": {
            "Type": "AWS::S3::Bucket",
            "Properties": {
                "BucketName": GDAX_TRADER_HOST,
                "AccessControl": "PublicRead",
                "WebsiteConfiguration": {
                    "IndexDocument": "index.html"
                }
            }
        },

        "Zone": {
            "Type": "AWS::Route53::HostedZone",
            "Properties": {
                "Name": DOMAIN
            }
        },

        "Hosts": {
            "Type": "AWS::Route53::RecordSetGroup",
            "Properties": {
                "HostedZoneName": DOMAIN + ".",
                "RecordSets": [

                    # Base
                    {
                        "Name": SHELL_HOST + ".",
                        "Type": "A",
                        "TTL": "60",
                        "ResourceRecords": [{"Ref": "IPAddress"}]
                    },
                    {
                        "Name": DOMAIN + ".",
                        "Type": "MX",
                        "TTL": "60",
                        "ResourceRecords": [
                            "10 {}.".format(MX),
                        ]
                    },
                    {
                        "Name": "quuux.org.",
                        "Type": "TXT",
                        "TTL": "60",
                        "ResourceRecords": [
                            "\"v=spf1 mx -all\"",
                            "\"google-site-verification=Jkx3pb3aspcyfy4-GVUtFkWB4ug24Q-bvfFX14qFGHw\"",
                        ]
                    },
                    {
                        "Name": "mail._domainkey.quuux.org.",
                        "Type": "TXT",
                        "TTL": "60",
                        "ResourceRecords": [
                            "\"v=DKIM1; k=rsa; t=y; p=MIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQDF0Y5593vEcohWnswvrcLcsh6Jze6AVfpxsSkAh06d9ulb3NMlwdPPJ/Z0/GfjM5WNrMK9UpbgBo+s/UrfJpt8uTcy607Xe5Fxvwf7ZdV7TB6tIbrGOudhwt3dJa3oEndomscG4yuactzJk8IBIM6le7eHfmJAr42nBnhnY5/OmQIDAQAB\""
                        ]

                    },

                    # Knapsack
                    {
                        "Name": KNAPSACK_WEB_HOST + ".",
                        "Type": "CNAME",
                        "TTL": "60",
                        "ResourceRecords": [KNAPSACK_WEB_HOST + ".s3-website-us-east-1.amazonaws.com"],
                    },
                    {
                        "Name": "knapsack-api.quuux.org.",
                        "Type": "A",
                        "TTL": "60",
                        "ResourceRecords": [{"Ref": "IPAddress"}]
                    },

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
                    "To": "22",
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
        "InboundHTTPNetworkAclEntry": {
            "Type": "AWS::EC2::NetworkAclEntry",
            "Properties": {
                "CidrBlock": "0.0.0.0/0",
                "Egress": "false",
                "NetworkAclId": {"Ref": "NetworkAcl"},
                "PortRange": {
                    "From": "80",
                    "To": "80"
                },
                "Protocol": "6",
                "RuleAction": "allow",
                "RuleNumber": "103"
            }
        },
        "InboundHTTPSNetworkAclEntry": {
            "Type": "AWS::EC2::NetworkAclEntry",
            "Properties": {
                "CidrBlock": "0.0.0.0/0",
                "Egress": "false",
                "NetworkAclId": {"Ref": "NetworkAcl"},
                "PortRange": {
                    "From": "443",
                    "To": "443"
                },
                "Protocol": "6",
                "RuleAction": "allow",
                "RuleNumber": "104"
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
                        "ToPort": "22",
                        "IpProtocol": "tcp",
                    },
                    {
                        "CidrIp": "0.0.0.0/0",
                        "FromPort": "25",
                        "IpProtocol": "tcp",
                        "ToPort": "25"
                    },
                    {
                        "CidrIp": "0.0.0.0/0",
                        "FromPort": "80",
                        "IpProtocol": "tcp",
                        "ToPort": "80"
                    },
                    {
                        "CidrIp": "0.0.0.0/0",
                        "FromPort": "443",
                        "IpProtocol": "tcp",
                        "ToPort": "443"
                    },
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
        },
    }
}

