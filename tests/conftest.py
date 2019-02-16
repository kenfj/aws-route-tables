import json

import boto3
import pytest


def fixtures_vpcs():
    with open("fixtures/vpcs.json") as f:
        return json.load(f)


def fixtures_subnets():
    with open("fixtures/subnets.json") as f:
        return json.load(f)


def fixtures_route_tables():
    with open("fixtures/route_tables.json") as f:
        return json.load(f)


def fixtures_vpc_peering_connections():
    with open("fixtures/vpc_peering_connections.json") as f:
        return json.load(f)


@pytest.fixture(autouse=True)
def setup_mock_boto3(monkeypatch):
    class MockBoto3(object):
        def __init__(self, service_name):
            self.service_name = service_name

        @staticmethod
        def describe_vpcs():
            return fixtures_vpcs()

        @staticmethod
        def describe_subnets():
            return fixtures_subnets()

        @staticmethod
        def describe_route_tables():
            return fixtures_route_tables()

        @staticmethod
        def describe_vpc_peering_connections():
            return fixtures_vpc_peering_connections()

    def mock_client(service_name):
        return MockBoto3(service_name)

    monkeypatch.setattr(boto3, "client", mock_client)
