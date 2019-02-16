import json

import boto3
import pytest

from aws_resources import AWSResource, VPCs, Subnets, RouteTables, VpcPeeringConnection


class TestAWSResource(object):
    @pytest.fixture
    def vpc(self):
        with open("fixtures/vpcs.json") as f:
            data = json.load(f)
        return data["Vpcs"]

    def test_aws_resource(self, vpc):
        assert AWSResource._get_name(vpc[0]) == "cvpn_test_vpc_cvpn"
        assert (
            AWSResource._cidr_str(vpc[0]["CidrBlock"])
            == "10.0.0.0/16 (10.0.0.1-10.0.255.254)"
        )


class TestVPCs(object):
    def test_vpc(self, setup_mock_boto3):
        client = boto3.client("ec2")
        vpcs = VPCs(client)

        assert vpcs[0].CidrBlockAssociationSet[0].CidrBlockState.State == "associated"
        assert (
            str(vpcs[0])
            == "vpc-03b96307a33428987  cvpn_test_vpc_cvpn  10.0.0.0/16 (10.0.0.1-10.0.255.254) (owner_id: 100000000000)"
        )
        assert (
            str(vpcs[1])
            == "vpc-04da3256                               172.31.0.0/16 (172.31.0.1-172.31.255.254) (owner_id: 100000000000)"
        )


class TestSubnets(object):
    def test_subnet(self, setup_mock_boto3):
        client = boto3.client("ec2")
        subnets = Subnets(client)

        assert subnets[0].VpcId == "vpc-03b96307a33428987"
        assert (
            str(subnets[0])
            == "    subnet-0d4b9e1cf2223169a  cvpn_test_subnet_cvpn  us-west-2a  10.0.1.0/24 (10.0.1.1-10.0.1.254)"
        )


class TestRouteTables(object):
    def test_route_table(self, setup_mock_boto3):
        client = boto3.client("ec2")
        pcx = VpcPeeringConnection(client)
        route_tables = RouteTables(client, pcx)

        assert route_tables[0].Associations[0].Main
        assert route_tables[1].is_associate("subnet-0d4b9e1cf2223169a")


class TestRoutes(object):
    def test_route(self, setup_mock_boto3):
        client = boto3.client("ec2")
        pcx = VpcPeeringConnection(client)
        route_tables = RouteTables(client, pcx)

        main_route_table = route_tables.find_route_table_main("vpc-04da3256")
        assert main_route_table.VpcId == "vpc-04da3256"
        assert main_route_table.RouteTableId == "rtb-e50a5a34"
        assert main_route_table.Associations[0].Main

        sub_route_tables = route_tables.find_route_tables_sub(
            "vpc-03b96307a33428987", "subnet-0d4b9e1cf2223169a"
        )
        assert sub_route_tables[0].VpcId == "vpc-03b96307a33428987"
        assert sub_route_tables[0].RouteTableId == "rtb-0edab5f8845653e29"
        assert sub_route_tables[0].Routes[0].GatewayId == "local"


class TestVpcPeeringConnection(object):
    def test_vpc_peering_connection(self, setup_mock_boto3):
        client = boto3.client("ec2")
        pcx = VpcPeeringConnection(client)

        assert pcx[0].AccepterVpcInfo.CidrBlock == "10.10.0.0/16"
        assert (
            pcx.find_peer_vpc("pcx-0eb928a29c9c63207", "vpc-085071b77f46b90cd")
            == "vpc_peering: 100000000000|us-west-2|vpc-03b96307a33428987|10.0.0.0/16"
        )
