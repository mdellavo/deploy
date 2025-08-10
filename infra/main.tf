terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 3.0"
    }
  }
}

variable "AWS_REGION" {
    default = "us-east-1"
}

variable "AWS_AZ" {
  default = "us-east-1b"
}

provider "aws" {
  region = var.AWS_REGION
}

resource "aws_vpc" "main" {
  assign_generated_ipv6_cidr_block = "false"
  cidr_block                       = "10.0.0.0/16"
  enable_dns_hostnames             = "true"
  enable_dns_support               = "true"
  instance_tenancy                 = "default"
}

resource "aws_subnet" "subnet" {
  assign_ipv6_address_on_creation                = "false"
  cidr_block                                     = "10.0.0.0/24"
  enable_dns64                                   = "false"
  enable_resource_name_dns_a_record_on_launch    = "false"
  enable_resource_name_dns_aaaa_record_on_launch = "false"
  ipv6_native                                    = "false"
  map_public_ip_on_launch                        = "false"
  private_dns_hostname_type_on_launch            = "ip-name"
  availability_zone                              = var.AWS_AZ
  vpc_id                                         = aws_vpc.main.id
}

resource "aws_subnet" "db_subnet" {
  assign_ipv6_address_on_creation                = "false"
  cidr_block                                     = "10.0.1.0/24"
  enable_dns64                                   = "false"
  enable_resource_name_dns_a_record_on_launch    = "false"
  enable_resource_name_dns_aaaa_record_on_launch = "false"
  ipv6_native                                    = "false"
  map_public_ip_on_launch                        = "false"
  private_dns_hostname_type_on_launch            = "ip-name"
  availability_zone                              = "us-east-1a"
  vpc_id                                         = aws_vpc.main.id
}

resource "aws_internet_gateway" "inet-gateway" {
  vpc_id = aws_vpc.main.id
}

resource "aws_main_route_table_association" "route-table-assoc-1" {
  route_table_id = aws_route_table.route-table-1.id
  vpc_id         = aws_vpc.main.id
}

resource "aws_route_table" "route-table-1" {
  vpc_id = aws_vpc.main.id
}

resource "aws_route_table" "route-table-2" {
  route {
    cidr_block = "0.0.0.0/0"
    gateway_id = aws_internet_gateway.inet-gateway.id
  }

  vpc_id = aws_vpc.main.id
}

resource "aws_route_table_association" "route-table-assoc-2" {
  route_table_id = aws_route_table.route-table-2.id
  subnet_id      = aws_subnet.subnet.id
}

resource "aws_security_group" "default-sg" {
  description = "default VPC security group"

  egress {
    cidr_blocks = ["0.0.0.0/0"]
    from_port   = "0"
    protocol    = "-1"
    self        = "false"
    to_port     = "0"
  }

  ingress {
    from_port = "0"
    protocol  = "-1"
    self      = "true"
    to_port   = "0"
  }

  name   = "default"
  vpc_id = aws_vpc.main.id
}

resource "aws_security_group" "frink-sg" {
  description = "Enable SSH access via port 22"

  egress {
    cidr_blocks = ["0.0.0.0/0"]
    from_port   = "0"
    protocol    = "-1"
    self        = "false"
    to_port     = "0"
  }

  ingress {
    cidr_blocks = ["0.0.0.0/0"]
    from_port   = "22"
    protocol    = "tcp"
    self        = "false"
    to_port     = "22"
  }

  ingress {
    cidr_blocks = ["0.0.0.0/0"]
    from_port   = "25"
    protocol    = "tcp"
    self        = "false"
    to_port     = "25"
  }

  ingress {
    cidr_blocks = ["0.0.0.0/0"]
    from_port   = "443"
    protocol    = "tcp"
    self        = "false"
    to_port     = "443"
  }

  ingress {
    cidr_blocks = ["0.0.0.0/0"]
    from_port   = "7777"
    protocol    = "tcp"
    self        = "false"
    to_port     = "7777"
  }

  ingress {
    cidr_blocks = ["0.0.0.0/0"]
    from_port   = "8"
    protocol    = "icmp"
    self        = "false"
    to_port     = "-1"
  }

  ingress {
    cidr_blocks = ["0.0.0.0/0"]
    from_port   = "80"
    protocol    = "tcp"
    self        = "false"
    to_port     = "80"
  }

  ingress {
    cidr_blocks = ["0.0.0.0/0"]
    from_port   = "8448"
    protocol    = "tcp"
    self        = "false"
    to_port     = "8448"
  }

  ingress {
    cidr_blocks = ["0.0.0.0/0"]
    from_port   = "9999"
    protocol    = "tcp"
    self        = "false"
    to_port     = "9999"
  }

  ingress {
    cidr_blocks = ["0.0.0.0/0"]
    from_port   = "587"
    protocol    = "tcp"
    self        = "false"
    to_port     = "587"
  }

  ingress {
    cidr_blocks = ["0.0.0.0/0"]
    from_port   = "993"
    protocol    = "tcp"
    self        = "false"
    to_port     = "993"
  }

  ingress {
    cidr_blocks = ["10.0.0.0/16"]
    from_port   = "5432"
    protocol    = "tcp"
    self        = "false"
    to_port     = "5432"
  }

  name   = "shell-InstanceSecurityGroup-12UQCNCVQ1481"
  vpc_id = aws_vpc.main.id
}

resource "aws_network_acl" "acl-1" {
  egress {
    action     = "allow"
    cidr_block = "0.0.0.0/0"
    from_port  = "0"
    icmp_code  = "0"
    icmp_type  = "0"
    protocol   = "-1"
    rule_no    = "100"
    to_port    = "0"
  }

  ingress {
    action     = "allow"
    cidr_block = "0.0.0.0/0"
    from_port  = "0"
    icmp_code  = "0"
    icmp_type  = "0"
    protocol   = "-1"
    rule_no    = "100"
    to_port    = "0"
  }

  subnet_ids = [aws_subnet.subnet.id]
  vpc_id     = aws_vpc.main.id
}

resource "aws_network_acl" "acl-2" {

  ingress {
    action     = "allow"
    cidr_block = "0.0.0.0/0"
    from_port  = "22"
    icmp_code  = "0"
    icmp_type  = "0"
    protocol   = "6"
    rule_no    = "101"
    to_port    = "22"
  }

  ingress {
    action     = "allow"
    cidr_block = "0.0.0.0/0"
    from_port  = "25"
    icmp_code  = "0"
    icmp_type  = "0"
    protocol   = "6"
    rule_no    = "102"
    to_port    = "25"
  }

  ingress {
    action     = "allow"
    cidr_block = "0.0.0.0/0"
    from_port  = "443"
    icmp_code  = "0"
    icmp_type  = "0"
    protocol   = "6"
    rule_no    = "104"
    to_port    = "443"
  }

  ingress {
    action     = "allow"
    cidr_block = "0.0.0.0/0"
    from_port  = "7777"
    icmp_code  = "0"
    icmp_type  = "0"
    protocol   = "6"
    rule_no    = "109"
    to_port    = "7777"
  }

  ingress {
    action     = "allow"
    cidr_block = "0.0.0.0/0"
    from_port  = "80"
    icmp_code  = "0"
    icmp_type  = "0"
    protocol   = "6"
    rule_no    = "103"
    to_port    = "80"
  }

  ingress {
    action     = "allow"
    cidr_block = "0.0.0.0/0"
    from_port  = "8080"
    icmp_code  = "0"
    icmp_type  = "0"
    protocol   = "6"
    rule_no    = "108"
    to_port    = "8080"
  }

  ingress {
    action     = "allow"
    cidr_block = "0.0.0.0/0"
    from_port  = "8448"
    icmp_code  = "0"
    icmp_type  = "0"
    protocol   = "6"
    rule_no    = "110"
    to_port    = "8448"
  }

  ingress {
    action     = "allow"
    cidr_block = "0.0.0.0/0"
    from_port  = "9999"
    icmp_code  = "0"
    icmp_type  = "0"
    protocol   = "6"
    rule_no    = "106"
    to_port    = "9999"
  }

  ingress {
    action     = "allow"
    cidr_block = "0.0.0.0/0"
    from_port  = "587"
    icmp_code  = "0"
    icmp_type  = "0"
    protocol   = "6"
    rule_no    = "120"
    to_port    = "587"
  }

  ingress {
    action     = "allow"
    cidr_block = "0.0.0.0/0"
    from_port  = "993"
    icmp_code  = "0"
    icmp_type  = "0"
    protocol   = "6"
    rule_no    = "121"
    to_port    = "993"
  }

  vpc_id = aws_vpc.main.id
}

resource "aws_instance" "ralph" {
  ami                         = "ami-0bcb08446fd149731"
  associate_public_ip_address = "true"
  availability_zone           = var.AWS_AZ

  capacity_reservation_specification {
    capacity_reservation_preference = "open"
  }

  cpu_core_count       = "1"
  cpu_threads_per_core = "1"

  credit_specification {
    cpu_credits = "unlimited"
  }

  disable_api_termination = "false"
  ebs_optimized           = "false"

  enclave_options {
    enabled = "false"
  }

  get_password_data                    = "false"
  hibernation                          = "false"
  instance_initiated_shutdown_behavior = "stop"
  instance_type                        = "t4g.small"
  ipv6_address_count                   = "0"
  key_name                             = "marc new"

  metadata_options {
    http_endpoint               = "enabled"
    http_put_response_hop_limit = "1"
    http_tokens                 = "optional"
    instance_metadata_tags      = "disabled"
  }

  monitoring = "false"
  private_ip = "10.0.0.22"

  root_block_device {
    delete_on_termination = "true"
    encrypted             = "false"
    volume_size           = "64"
    volume_type           = "gp2"
  }

  source_dest_check = "true"
  subnet_id         = aws_subnet.subnet.id

  tags = {
    Name = "Ralph"
  }

  tags_all = {
    Name = "Ralph"
  }

  tenancy                = "default"
  vpc_security_group_ids = [
    aws_security_group.frink-sg.id
  ]
}

resource "aws_eip" "ip-ralph" {
  instance             = aws_instance.ralph.id
  network_border_group = var.AWS_REGION
  public_ipv4_pool     = "amazon"
  vpc                  = "true"
}

resource "aws_db_subnet_group" "main" {
  name       = "main"
  subnet_ids = [aws_subnet.subnet.id, aws_subnet.db_subnet.id]

  tags = {
    Name = "Main DB subnet group"
  }
}

resource "aws_db_instance" "postgres" {
  allocated_storage           = 20
  storage_type               = "gp2"
  engine                     = "postgres"
  engine_version             = "17.5"
  instance_class             = "db.t4g.micro"
  identifier                 = "postgres"
  username                   = "postgres"
  password                   = "postgrespassword"
  availability_zone          = var.AWS_AZ
  db_subnet_group_name       = aws_db_subnet_group.main.name
  vpc_security_group_ids     = [aws_security_group.frink-sg.id]
  backup_retention_period    = 0
  multi_az                   = false
  publicly_accessible        = false
  storage_encrypted          = false
  skip_final_snapshot        = true
  deletion_protection        = false

  tags = {
    Name = "PostgreSQL Database"
  }
}

# S3 Buckets

resource "aws_s3_bucket" "logs-quuux" {
  arn                 = "arn:aws:s3:::logs-quuux"
  bucket              = "logs-quuux"
}

// marcdellavolpe.com

resource "aws_route53_zone" "zone-marcdellavolpe-com" {
  name = "marcdellavolpe.com"
}

resource "aws_route53_record" "dns-marcdellavolpe-com-a" {
  name    = "marcdellavolpe.com"
  type    = "A"
  ttl     = "60"
  records = [aws_eip.ip-ralph.public_ip]
  zone_id = aws_route53_zone.zone-marcdellavolpe-com.zone_id
}

resource "aws_route53_record" "dns-marcdellavolpe-com-mx" {
  name    = "marcdellavolpe.com"
  records = ["10 mail.quuux.org."]
  ttl     = "60"
  type    = "MX"
  zone_id = aws_route53_zone.zone-marcdellavolpe-com.zone_id
}

resource "aws_route53_record" "dns-marcdellavolpe-com-txt" {
  name    = "marcdellavolpe.com"
  records = ["google-site-verification=KasvFeWlCVAUYQ2xIU8ZabVi8SVbxwOieWQVEV6uF70", "v=spf1 mx -all"]
  ttl     = "60"
  type    = "TXT"
  zone_id = aws_route53_zone.zone-marcdellavolpe-com.zone_id
}

module "marcdellavolpe-com" {
  source = "./modules/s3-website"
  bucket = "marcdellavolpe.com"
}

// quuux.org

resource "aws_route53_zone" "zone-quuux-org" {
  name = "quuux.org"
}

resource "aws_route53_record" "dns-quuux-org-mx" {
  name    = "quuux.org"
  records = ["10 mail.quuux.org."]
  ttl     = "60"
  type    = "MX"
  zone_id = aws_route53_zone.zone-quuux-org.zone_id
}

resource "aws_route53_record" "dns-ralph-quuux-org-a" {
  name    = "ralph.quuux.org"
  records = [aws_eip.ip-ralph.public_ip]
  ttl     = "60"
  type    = "A"
  zone_id = aws_route53_zone.zone-quuux-org.zone_id
}

resource "aws_route53_record" "dns-mail-quuux-org-a" {
  name    = "mail.quuux.org"
  records = [aws_eip.ip-ralph.public_ip]
  ttl     = "60"
  type    = "A"
  zone_id = aws_route53_zone.zone-quuux-org.zone_id
}

resource "aws_route53_record" "dns-liminal-quuux-org-a" {
  name    = "liminal.quuux.org"
  records = [aws_eip.ip-ralph.public_ip]
  ttl     = "60"
  type    = "A"
  zone_id = aws_route53_zone.zone-quuux-org.zone_id
}

resource "aws_route53_record" "dns-quuux-org-a" {
  name    = "quuux.org"
  records = [aws_eip.ip-ralph.public_ip]
  ttl     = "60"
  type    = "A"
  zone_id = aws_route53_zone.zone-quuux-org.zone_id
}

resource "aws_route53_record" "dns-quuux-org-txt" {
  name    = "quuux.org"
  records = ["google-site-verification=Jkx3pb3aspcyfy4-GVUtFkWB4ug24Q-bvfFX14qFGHw"]
  ttl     = "60"
  type    = "TXT"
  zone_id = aws_route53_zone.zone-quuux-org.zone_id
}

resource "aws_route53_record" "dns-rogue-quuux-org-a" {
  name    = "rogue.quuux.org"
  records = [aws_eip.ip-ralph.public_ip]
  ttl     = "60"
  type    = "A"
  zone_id = aws_route53_zone.zone-quuux-org.zone_id
}

resource "aws_route53_record" "dns-rogue-api-quuux-org-a" {
  name    = "rogue-api.quuux.org"
  records = [aws_eip.ip-ralph.public_ip]
  ttl     = "60"
  type    = "A"
  zone_id = aws_route53_zone.zone-quuux-org.zone_id
}

// Tailscale IPs

resource "aws_route53_record" "dns-mojo-ts-quuux-org-a" {
  name    = "mojo.ts.quuux.org"
  records = ["100.82.224.98"]
  ttl     = "60"
  type    = "A"
  zone_id = aws_route53_zone.zone-quuux-org.zone_id
}

resource "aws_route53_record" "dns-atomic-ts-quuux-org-a" {
  name    = "atomic.ts.quuux.org"
  records = ["100.89.171.89"]
  ttl     = "60"
  type    = "A"
  zone_id = aws_route53_zone.zone-quuux-org.zone_id
}

resource "aws_route53_record" "dns-synology-ts-quuux-org-a" {
  name    = "synology.ts.quuux.org"
  records = ["100.106.167.130"]
  ttl     = "60"
  type    = "A"
  zone_id = aws_route53_zone.zone-quuux-org.zone_id
}

resource "aws_route53_record" "dns-lisa-ts-quuux-org-a" {
  name    = "lisa.ts.quuux.org"
  records = ["100.107.92.17"]
  ttl     = "60"
  type    = "A"
  zone_id = aws_route53_zone.zone-quuux-org.zone_id
}

resource "aws_route53_record" "dns-maggie-ts-quuux-org-a" {
  name    = "maggie.ts.quuux.org"
  records = ["100.109.254.49"]
  ttl     = "60"
  type    = "A"
  zone_id = aws_route53_zone.zone-quuux-org.zone_id
}

resource "aws_route53_record" "dns-marge-ts-quuux-org-a" {
  name    = "marge.ts.quuux.org"
  records = ["100.70.223.52"]
  ttl     = "60"
  type    = "A"
  zone_id = aws_route53_zone.zone-quuux-org.zone_id
}

module "liminal-quuux-org" {
  source = "./modules/s3-website"
  bucket = "liminal.quuux.org"
}

module "rogue-quuux-org" {
  source = "./modules/s3-website"
  bucket = "rogue.quuux.org"
}

// p.ound.town

resource "aws_route53_zone" "zone-ound-town" {
  name = "ound.town"
}


resource "aws_route53_record" "dns-p-ound-town-a" {
  name    = "p.ound.town"
  records = [aws_eip.ip-ralph.public_ip]
  ttl     = "60"
  type    = "A"
  zone_id = aws_route53_zone.zone-ound-town.zone_id
}

// consolejockey.life

resource "aws_route53_zone" "zone-consolejockey-life" {
  name = "consolejockey.life"
}

resource "aws_route53_record" "dns-consolejockey-life-a" {
  name    = "consolejockey.life"
  type    = "A"
  ttl     = "60"
  records = [aws_eip.ip-ralph.public_ip]
  zone_id = aws_route53_zone.zone-consolejockey-life.zone_id
}

// terminaljunkie.lol

resource "aws_route53_zone" "zone-terminaljunkie-lol" {
  name = "terminaljunkie.lol"
}

resource "aws_route53_record" "dns-terminaljunkie-lol-a" {
  name    = "terminaljunkie.lol"
  type    = "A"
  ttl     = "60"
  records = [aws_eip.ip-ralph.public_ip]
  zone_id = aws_route53_zone.zone-terminaljunkie-lol.zone_id
}

// Sites

resource "aws_route53_zone" "zone-fucknorcross-com" {
  name = "fucknorcross.com"
}

resource "aws_route53_record" "dns-fucknorcross-com-a" {
  name    = "fucknorcross.com"
  type    = "A"
  ttl     = "60"
  records = [aws_eip.ip-ralph.public_ip]
  zone_id = aws_route53_zone.zone-fucknorcross-com.zone_id
}

resource "aws_route53_zone" "zone-fucksweeney-com" {
  name = "fucksweeney.com"
}

resource "aws_route53_record" "dns-fucksweeney-com-a" {
  name    = "fucksweeney.com"
  type    = "A"
  ttl     = "60"
  records = [aws_eip.ip-ralph.public_ip]
  zone_id = aws_route53_zone.zone-fucksweeney-com.zone_id
}

module "fucknorcross-com" {
  source = "./modules/s3-website"
  bucket = "fucknorcross.com"

}

module "fucksweeney-com" {
  source = "./modules/s3-website"
  bucket = "fucksweeney.com"
}

resource "aws_route53_record" "dns-fucknorcross-com-ns" {
  name    = "fucknorcross.com"
  records = [
    "ns-1342.awsdns-39.org.",
    "ns-1860.awsdns-40.co.uk.",
    "ns-50.awsdns-06.com.",
    "ns-513.awsdns-00.net.",
  ]
  ttl     = 172800
  type    = "NS"
  zone_id = aws_route53_zone.zone-fucknorcross-com.zone_id
}

resource "aws_route53_record" "dns-fucknorcross-com-soa" {
  name    = "fucknorcross.com"
  records = [
    "ns-513.awsdns-00.net. awsdns-hostmaster.amazon.com. 1 7200 900 1209600 86400",
  ]
  ttl     = 900
  type    = "SOA"
  zone_id = aws_route53_zone.zone-fucknorcross-com.zone_id
}

resource "aws_route53_record" "dns-fucksweeney-com-ns" {
  name    = "fucksweeney.com"
  records = [
    "ns-1323.awsdns-37.org.",
    "ns-2033.awsdns-62.co.uk.",
    "ns-325.awsdns-40.com.",
    "ns-938.awsdns-53.net.",
  ]
  ttl     = 172800
  type    = "NS"
  zone_id = aws_route53_zone.zone-fucksweeney-com.zone_id
}

resource "aws_route53_record" "dns-fucksweeney-com-soa" {
  name    = "fucksweeney.com"
  records = [
    "ns-2033.awsdns-62.co.uk. awsdns-hostmaster.amazon.com. 1 7200 900 1209600 86400",
  ]
  ttl     = 900
  type    = "SOA"
  zone_id = aws_route53_zone.zone-fucksweeney-com.zone_id
}


resource "aws_route53_record" "dns-ound-town-ns" {
  name    = "ound.town"
  records = ["ns-1432.awsdns-51.org.", "ns-1609.awsdns-09.co.uk.", "ns-330.awsdns-41.com.", "ns-910.awsdns-49.net."]
  ttl     = "172800"
  type    = "NS"
  zone_id = aws_route53_zone.zone-ound-town.zone_id
}

resource "aws_route53_record" "dns-ound-town-soa" {
  name    = "ound.town"
  records = ["ns-1609.awsdns-09.co.uk. awsdns-hostmaster.amazon.com. 1 7200 900 1209600 86400"]
  ttl     = "900"
  type    = "SOA"
  zone_id = aws_route53_zone.zone-ound-town.zone_id
}

resource "aws_route53_record" "dns-marcdellavolpe-com-ns" {
  name    = "marcdellavolpe.com"
  records = [
    "ns-1409.awsdns-48.org.",
    "ns-1711.awsdns-21.co.uk.",
    "ns-364.awsdns-45.com.",
    "ns-576.awsdns-08.net.",
  ]
  ttl     = 172800
  type    = "NS"
  zone_id = aws_route53_zone.zone-marcdellavolpe-com.zone_id
}

resource "aws_route53_record" "dns-marcdellavolpe-com-soa" {
  name    = "marcdellavolpe.com"
  records = [
    "ns-364.awsdns-45.com. awsdns-hostmaster.amazon.com. 1 7200 900 1209600 86400",
  ]
  ttl     = 900
  type    = "SOA"
  zone_id = aws_route53_zone.zone-marcdellavolpe-com.zone_id
}


resource "aws_route53_record" "dns-quuux-org-ns" {
  name    = "quuux.org"
  records = [
    "ns-1346.awsdns-40.org.",
    "ns-141.awsdns-17.com.",
    "ns-1542.awsdns-00.co.uk.",
    "ns-993.awsdns-60.net.",
  ]
  ttl     = 172800
  type    = "NS"
  zone_id = aws_route53_zone.zone-quuux-org.zone_id
}

resource "aws_route53_record" "dns-quuux-org-soa" {
  name    = "quuux.org"
  records = [
    "ns-141.awsdns-17.com. awsdns-hostmaster.amazon.com. 1 7200 900 1209600 86400",
  ]
  ttl     = 900
  type    = "SOA"
  zone_id = aws_route53_zone.zone-quuux-org.zone_id
}
