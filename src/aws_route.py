#!/usr/bin/env python
import argparse
import sys

from boto3.session import Session

from aws_route_app import app

parser = argparse.ArgumentParser()
parser.add_argument("--region_name", help="region_name")
parser.add_argument("--profile_name", help="profile_name")

args = parser.parse_args()


def create_boto3_client(service_name):
    region = args.region_name or Session().region_name
    profile = args.profile_name or Session().profile_name

    session = Session(region_name=region, profile_name=profile)
    client = session.client(service_name)

    return client


#
# AWS routes: show route tables in each VPC/Subnet
#
def main():
    client = create_boto3_client("ec2")
    print(app(client))


if __name__ == "__main__":
    sys.exit(main())
