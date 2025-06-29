import os.path

CONFIGS_PATH = os.path.join(os.path.dirname(__file__), "..", "config")

LOGGING_BUCKET = "logs-quuux"


def hosted_zone(zone):
    return {
        "Type": "AWS::Route53::HostedZone",
        "Properties": {
            "Name": zone
        }
    }

def s3_bucket(name, website=False):
    rv = {
        "Type": "AWS::S3::Bucket",
        "Properties": {
            "BucketName": name,
            "AccessControl": "PublicRead",
        }
    }
    if website:
        rv["Properties"]["WebsiteConfiguration"] = {
            "IndexDocument": "index.html",
        }
    return rv


def s3_hosted_zone_alias(domain):
    return {
        "Name": f"{domain}.",
        "Type": "A",
        "AliasTarget": {
            "HostedZoneId": "Z3AQBSTGFYJSTF",
            "DNSName": "s3-website-us-east-1.amazonaws.com"
        }
    }

def zone_records(hosted_zone_id, zone_name, records):
    return {
        "Type": "AWS::Route53::RecordSetGroup",
        "DependsOn": hosted_zone_id,
        "Properties": {
            "HostedZoneName": f"{zone_name}.",
            "RecordSets": records
        },
    }


def address_record(domain, ref, ttl="60"):
    return {
        "Name": f"{domain}.",
        "Type": "A",
        "TTL": ttl,
        "ResourceRecords": [{"Ref": ref}]
    }


WEBSITE_STACK = {
    "AWSTemplateFormatVersion": "2010-09-09",
    "Description": "QUUUX Resources",

    "Resources": {
        "ZoneMarcDellaVolpe": hosted_zone("marcdellavolpe.com"),
        "BucketMarcDellaVolpe": s3_bucket("marcdellavolpe.com", website=True),
        "HostsMarcDellaVolpe": zone_records("ZoneMarcDellaVolpe", "marcdellavolpe.com", [
            s3_hosted_zone_alias("marcdellavolpe.com"),
            {
                "Name": "marcdellavolpe.com",
                "Type": "TXT",
                "TTL": "60",
                "ResourceRecords": [
                    "\"google-site-verification=KasvFeWlCVAUYQ2xIU8ZabVi8SVbxwOieWQVEV6uF70\"",
                    "\"v=spf1 mx -all\"",
                ]
            },
        ]),
        "ZoneFuckSweeney": hosted_zone("fucksweeney.com"),
        "BucketFuckSweeney": s3_bucket("fucksweeney.com", website=True),
        "HostsFuckSweeney": zone_records("ZoneFuckSweeney", "fucksweeney.com", [s3_hosted_zone_alias("fucksweeney.com")]),

        "ZoneFuckNorcross": hosted_zone("fucknorcross.com"),
        "BucketFuckNorcross": s3_bucket("fucknorcross.com", website=True),
        "HostsFuckNorcross": zone_records("ZoneFuckNorcross", "fucknorcross.com", [s3_hosted_zone_alias("fucknorcross.com")]),
    }
}

# Shell config

REGION = "us-east-1"
AZ = REGION + "b"

HOST_SIZE = "t3.nano"
HOST_AMI = "ami-0857dde146952200b"


SHELL_STACK = {
    "AWSTemplateFormatVersion": "2010-09-09",
    "Description": "Shell",

    "Outputs": {

        "HostInstanceId": {
            "Description": "Host (frink) instance",
            "Value": {"Ref": "Host"}
        },
        "HostPublicDNS": {
            "Description": "Host dns",
            "Value": {"Fn::GetAtt": ["Host", "PublicDnsName"]}
        },
        "HostPublicIP": {
            "Description": "Host ip",
            "Value": {"Fn::GetAtt": ["Host", "PublicIp"]}
        },

    },
    "Resources": {

        "Host": {
            "Type": "AWS::EC2::Instance",
            "Properties": {
                "ImageId": HOST_AMI,
                "InstanceType": HOST_SIZE,
                "KeyName": "marc new",
                "NetworkInterfaces": [
                    {
                        "AssociatePublicIpAddress": "true",
                        "DeleteOnTermination": "true",
                        "DeviceIndex": "0",
                        "GroupSet": [{"Ref": "InstanceSecurityGroup"}],
                        "SubnetId": {"Ref": "Subnet"}
                    }
                ],
                "BlockDeviceMappings": [
                    {
                        "DeviceName": "/dev/sda1",
                        "Ebs": {"VolumeSize": "64"}
                    }
                ],
                "Volumes": [],
                "Tags": [
                    {"Key": "Name", "Value": "Host"},
                ]
            },
        },

        "Zone": hosted_zone("quuux.org"),
        "BucketRogue": s3_bucket("rogue.quuux.org", website=True),
        "BucketLiminal": s3_bucket("liminal.quuux.org", website=True),

        "Hosts": zone_records("Zone", "quuux.org", [

                    {
                        "Name": "quuux.org.",
                        "Type": "A",
                        "TTL": "60",
                        "ResourceRecords": [{"Ref": "HostIPAddress"}]
                    },

                    # Legacy
                    {
                        "Name": "snake.quuux.org.",
                        "Type": "A",
                        "TTL": "60",
                        "ResourceRecords": [{"Ref": "HostIPAddress"}]
                    },

                    {
                        "Name": "quuux.org",
                        "Type": "TXT",
                        "TTL": "60",
                        "ResourceRecords": [
                            "\"google-site-verification=Jkx3pb3aspcyfy4-GVUtFkWB4ug24Q-bvfFX14qFGHw\"",
                        ]
                    },

                    #
                    {
                        "Name": "frink.quuux.org.",
                        "Type": "A",
                        "TTL": "60",
                        "ResourceRecords": [{"Ref": "HostIPAddress"}]
                    },


                    # Rogue
                    {
                        "Name": "rogue.quuux.org.",
                        "Type": "A",
                        "TTL": "60",
                        "ResourceRecords": [{"Ref": "HostIPAddress"}]
                    },
                    {
                        "Name": "rogue-api.quuux.org.",
                        "Type": "A",
                        "TTL": "60",
                        "ResourceRecords": [{"Ref": "HostIPAddress"}]
                    },

                    # Liminal
                    {
                        "Name": "liminal.quuux.org.",
                        "Type": "A",
                        "TTL": "60",
                        "ResourceRecords": [{"Ref": "HostIPAddress"}]
                    },

                    # Homephone
                    {
                        "Name": "homephone.quuux.org.",
                        "Type": "A",
                        "TTL": "60",
                        "ResourceRecords": [{"Ref": "HostIPAddress"}]
                    },

                    # Atomic
                    {
                        "Name": "atomic.quuux.org.",
                        "Type": "A",
                        "TTL": "60",
                        "ResourceRecords": [{"Ref": "HostIPAddress"}]
                    },

        ]),
        "PoundtownZone": hosted_zone("ound.town"),

        "PoundtownHosts": {
            "Type": "AWS::Route53::RecordSetGroup",
            "Properties": {
                "HostedZoneName": "ound.town.",
                "RecordSets": [
                    {
                        "Name": "p.ound.town.",
                        "Type": "A",
                        "TTL": "60",
                        "ResourceRecords": [{"Ref": "HostIPAddress"}]
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
        "HostIPAddress": {
            "Type": "AWS::EC2::EIP",
            "DependsOn": "AttachGateway",
            "Properties": {
                "Domain": "vpc",
                "InstanceId": {"Ref": "Host"}
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
        "InboundIRCSNetworkAclEntry": {
            "Type": "AWS::EC2::NetworkAclEntry",
            "Properties": {
                "CidrBlock": "0.0.0.0/0",
                "Egress": "false",
                "NetworkAclId": {"Ref": "NetworkAcl"},
                "PortRange": {
                    "From": "9999",
                    "To": "9999"
                },
                "Protocol": "6",
                "RuleAction": "allow",
                "RuleNumber": "106"
            }
        },
        "InboundRogueNetworkAclEntry": {
            "Type": "AWS::EC2::NetworkAclEntry",
            "Properties": {
                "CidrBlock": "0.0.0.0/0",
                "Egress": "false",
                "NetworkAclId": {"Ref": "NetworkAcl"},
                "PortRange": {
                    "From": "8080",
                    "To": "8080"
                },
                "Protocol": "6",
                "RuleAction": "allow",
                "RuleNumber": "108"
            }
        },
        "InboundIRCLinkNetworkAclEntry": {
            "Type": "AWS::EC2::NetworkAclEntry",
            "Properties": {
                "CidrBlock": "0.0.0.0/0",
                "Egress": "false",
                "NetworkAclId": {"Ref": "NetworkAcl"},
                "PortRange": {
                    "From": "7777",
                    "To": "7777"
                },
                "Protocol": "6",
                "RuleAction": "allow",
                "RuleNumber": "109"
            }
        },


        "InboundMatrixFederationNetworkAclEntry": {
            "Type": "AWS::EC2::NetworkAclEntry",
            "Properties": {
                "CidrBlock": "0.0.0.0/0",
                "Egress": "false",
                "NetworkAclId": {"Ref": "NetworkAcl"},
                "PortRange": {
                    "From": "8448",
                    "To": "8448"
                },
                "Protocol": "6",
                "RuleAction": "allow",
                "RuleNumber": "110"
            }
        },

        "InstanceSecurityGroup": {
            "Type": "AWS::EC2::SecurityGroup",
            "Properties": {
                "GroupDescription": "Enable SSH access via port 22",
                "SecurityGroupIngress": [
                    {
                        "IpProtocol" : "icmp",
                        "FromPort" : "8",
                        "ToPort" : "-1",
                        "CidrIp" : "0.0.0.0/0"
                    },
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
                    {
                        "CidrIp": "0.0.0.0/0",
                        "FromPort": "9999",
                        "IpProtocol": "tcp",
                        "ToPort": "9999"
                    },
                    {
                        "CidrIp": "0.0.0.0/0",
                        "FromPort": "7777",
                        "IpProtocol": "tcp",
                        "ToPort": "7777"
                    },
                    {
                        "CidrIp": "0.0.0.0/0",
                        "FromPort": "8448",
                        "IpProtocol": "tcp",
                        "ToPort": "8448"
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
