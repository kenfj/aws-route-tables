import boto3


def test_mock_boto3(setup_mock_boto3):
    client = boto3.client("ec2")

    vpcs = client.describe_vpcs()["Vpcs"]
    assert vpcs[0]["CidrBlock"] == "10.0.0.0/16"

    subnets = client.describe_subnets()["Subnets"]
    assert subnets[0]["CidrBlock"] == "172.31.0.0/20"

    route_tables = client.describe_route_tables()["RouteTables"]
    assert route_tables[0]["Routes"][0]["GatewayId"] == "local"

    pcx = client.describe_vpc_peering_connections()["VpcPeeringConnections"]
    assert pcx[0]["AccepterVpcInfo"]["CidrBlock"] == "10.10.0.0/16"
