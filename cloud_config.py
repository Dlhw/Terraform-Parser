# Any resource names with certain prefixes are consolidated into one node
AWS_CONSOLIDATED_NODES = [
    {
        "config": {
            "resource_name": "AWS Config",
            "import_location": "resource_classes.aws.network",
            "vpc": False,
            "edge_service": True,
        }
    },
    {
        "elastic_beanstalk": {
            "resource_name": "Elastic Beanstalk",
            "import_location": "resource_classes.aws.network",
            "vpc": False,
            "edge_service": True,
        }
    },
    {
        "aws_wafv2_web_acl": {
            "resource_name": "AWS WAF",
            "import_location": "resource_classes.aws.network",
            "vpc": False,
            "edge_service": True,
        }
    },
    {
        "aws_networkfirewall": {
            "resource_name": "AWS Network Firewall",
            "import_location": "resource_classes.aws.network",
            "vpc": False,
            "edge_service": True,
        }
    },
    {
        "aws_secretsmanager_secret": {
            "resource_name": "AWS Secrets Manager",
            "import_location": "resource_classes.aws.network",
            "vpc": False,
            "edge_service": True,
        }
    },
    {
        "cloudtrail": {
            "resource_name": "AWS CloudTrail",
            "import_location": "resource_classes.aws.network",
            "vpc": False,
            "edge_service": True,
        }
    },
    {
        "backup": {
            "resource_name": "AWS Backup",
            "import_location": "resource_classes.aws.network",
            "vpc": False,
            "edge_service": True,
        }
    },
    {
        "iam": {
            "resource_name": "AWS IAM",
            "import_location": "resource_classes.aws.network",
            "vpc": False,
            "edge_service": True,
        }
    },
    {
        "aws_s3_bucket": {
            "resource_name": "S3 bucket",
            "import_location": "resource_classes.aws.network",
            "vpc": False,
            "edge_service": True,
        }
    },
    {
        "aws_cloudfront_distribution": {
            "resource_name": "AWS CloudFront Distribution",
            "import_location": "resource_classes.aws.network",
            "vpc": False,
            "edge_service": True,
        }
    },
        {
        "aws_route53_resolver_firewall": {
            "resource_name": "Route 53 Resolver DNS firewall",
            "import_location": "resource_classes.aws.network",
            "vpc": False,
            "edge_service": True,
        }
    },
    {
        "aws_route53_record": {
            "resource_name": "AWS Route 53 DNS",
            "import_location": "resource_classes.aws.network",
            "vpc": False,
            "edge_service": True,
        }
    },
    {
        "aws_cloudwatch": {
            "resource_name": "AWS Cloudwatch",
            "import_location": "resource_classes.aws.management",
            "vpc": False,
        }
    },
    {
        "aws_api_gateway": {
            "resource_name": "aws_api_gateway_integration.gateway",
            "import_location": "resource_classes.aws.network",
            "vpc": False,
        }
    },
    {
        "aws_acm_certificate": {
            "resource_name": "aws_acm_certificate.acm",
            "import_location": "resource_classes.aws.security",
            "vpc": False,
        }
    },
    {
        "aws_ssm_parameter": {
            "resource_name": "aws_ssm_parameter.ssmparam",
            "import_location": "resource_classes.aws.management",
            "vpc": False,
        }
    },
    {
        "aws_dx": {
            "resource_name": "aws_dx_connection.directconnect",
            "import_location": "resource_classes.aws.network",
            "vpc": False,
            "edge_service": True,
        }
    },
    {
        "aws_lb": {
            "resource_name": "aws_lb.elb",
            "import_location": "resource_classes.aws.network",
            "vpc": True,
        }
    },
    {
        "aws_ecs": {
            "resource_name": "aws_ecs_service.ecs",
            "import_location": "resource_classes.aws.compute",
            "vpc": True,
        }
    },
    {
        "aws_internet_gateway": {
            "resource_name": "aws_internet_gateway.igw",
            "import_location": "resource_classes.aws.network",
            "vpc": True,
        }
    }, 
    {
        "aws_eip": {
            "resource_name": "aws_eip.eip",
            "import_location": "resource_classes.aws.network",
            "vpc": True,
        }
    },
    {
        "aws_efs_file_system": {
            "resource_name": "aws_efs_file_system.efs",
            "import_location": "resource_classes.aws.storage",
            "vpc": False,
        }
    }
]

# List of Group type nodes and order to draw them in
AWS_GROUP_NODES = [
    "aws_vpc",
    "aws_az",
    "aws_group",
    "aws_appautoscaling_target",
    "aws_subnet",
    "aws_security_group",
    "aws_network_acl",
    "tv_aws_onprem"
]

# Nodes to be drawn first inside the AWS Cloud but outside any subnets or VPCs
AWS_EDGE_NODES = [
    "aws_route53",
    "aws_cloudfront_distribution",
    "aws_internet_gateway",
    "aws_api_gateway",
    "aws_apigateway"
]

# Nodes outside Cloud boundary
AWS_OUTER_NODES = [
    "tv_aws_users",
    "tv_aws_internet"    
]

# Order to draw nodes - leave empty string list till last to denote everything else
AWS_DRAW_ORDER = [AWS_OUTER_NODES, AWS_EDGE_NODES, AWS_GROUP_NODES, AWS_CONSOLIDATED_NODES, [""]]

# List of prefixes where additional nodes should be created automatically
AWS_AUTO_ANNOTATIONS = [
    # {"aws_route53": {"link": ["tv_aws_users.users"], "arrow": "reverse"}},
    {"aws_dx": {"link": ["tv_aws_onprem.corporate_datacenter", "tv_aws_cgw.customer_gateway"], "arrow": "forward"}},
    {"aws_internet_gateway": {"link": ["tv_aws_internet.internet"], "arrow": "reverse"}},
    {"aws_nat_gateway": {"link": ["aws_internet_gateway.*"], "arrow": "forward"}},
    {"aws_ecs_service": {"link": ["aws_ecr_repository.ecr"], "arrow": "forward"}},
    {"aws_ecs_": {"link": ["aws_ecs_cluster.ecs"], "arrow": "forward"}},
    {"aws_lambda": {"link": ["aws_cloudwatch_log_group.cloudwatch"], "arrow": "forward"}}
]

# Variant icons for the same service - matches keyword in meta data and changes resource type
AWS_NODE_VARIANTS = {
    "aws_ecs_service": {"FARGATE": "aws_fargate", "EC2": "aws_ec2ecs"},
    "aws_lb": {"application": "aws_alb", "network": "aws_nlb"},
    "aws_rds": {"aurora": "aws_rds_aurora", "mysql": "aws_rds_mysql", "postgres": "aws_rds_postgres"},
    }

# Automatically reverse arrow direction for these resources
AWS_REVERSE_ARROW_LIST = [
    'aws_route53',
    'aws_cloudfront',
    'aws_vpc.',
    'aws_subnet.',
    'aws_iam_role.',
    'aws_lb'
]

AWS_IMPLIED_CONNECTIONS = {
    'certificate_arn': 'aws_acm_certificate.this',
    'container_definitions' : 'aws_ecr_repository',
    }

# List of special resources and handler function name
AWS_SPECIAL_RESOURCES = {
    'aws_cloudfront_distribution' : 'aws_handle_cloudfront_pregraph',
    'aws_subnet' : 'aws_handle_subnet_azs',
    'aws_appautoscaling_target' : 'aws_handle_autoscaling',
    'aws_efs_file_system' : 'aws_handle_efs',
    'aws_db_subnet' : 'aws_handle_dbsubnet',
    'aws_security_group' : 'aws_handle_sg', # place after db_subnet handler
    'aws_lb' : 'aws_handle_lb',
    'aws_' : 'aws_handle_sharedgroup'
}

AWS_SHARED_SERVICES = [
        "aws_acm_certificate",
        "aws_cloudwatch_log_group",
        "aws_ecr_repository",
        "aws_efs_file_system",
        "aws_ssm_parameter",
        "aws_eip",
        "aws_kms_key"
]

INCLUDE = [
    "aws",
    "aws_vpc",
    "aws_az",
    "aws_group",
    "aws_appautoscaling_target",
    "aws_subnet",
    # "aws_security_group",
    "tv_aws_onprem",
    "aws_acm_certificate",
    "aws_api_gateway_rest_api",
    "aws_apigatewayv2_api",
    "aws_cloudfront_distribution",
    "aws_route53_record",
    # "aws_internet_gateway",
    # "aws_nat_gateway",
    "aws_ecs_service",
    # "aws_lambda_function",
    "aws_lb",
    "aws_elb",
    "aws_alb",
    # "aws_elastic_beanstalk_application",
    # "aws_s3_bucket",
    # "aws_vpc_endpoint",
    "aws_instance",
    "aws_ec2_transit_gateway",
    "aws_ec2_transit_gateway_vpc_attachment",
    # "aws_cloudwatch_log_group",
    # "aws_cloudtrail",
    "aws_networkfirewall_firewall",
    "aws_route53_resolver_firewall_domain_list",
    # "aws_wafv2_web_acl",
    "aws_secretsmanager_secret",
    # "aws_backup_plan",
    "aws_network_acl",
    # "aws_iam_role",
    "aws_db_instance"
    ]

AWS_AUTO_LINKS = [
    {"aws_ec2_transit_gateway_vpc_attachment": {"link": ["aws_ec2_transit_gateway"], "arrow": "none"}}
]

SINGLE_NODES=[
    "config",
    "cloudtrail",
    "cloudwatch",
    "iam",
    "backup",
    "networkfirewall",
    "aws_wafv2_web_acl",
    "elastic_beanstalk"
]

EXCLUDE = [ 
            'var',
            'root',
            'output',
            'data',
            'local',
            "aws_iam",
            "aws_route_table",
            "aws_network_acl",
            'aws_alb_target_group',
            "aws_key_pair",
            "aws_autoscaling",
            "aws_launch_configuration",
            "aws_db_instance",
            "aws_db_parameter_group",
            "aws_db_subnet_group",
            "aws_security_group",
            "aws_ec2_transit_gateway_route_table",
            "aws_cloudfront_origin_access_identity",
            "aws_route53_resolver_rule_association",
            "aws_route53_zone",
            "aws_eip",
            "aws_api_gateway_deployment",
            "aws_api_gateway_resource",
            "aws_api_gateway_stage",
            "aws_ec2_transit_gateway_vpc_ttachment_accepter",
            "aws_acm_certificate_validation"
            ]       