import boto3

from aws_route_app import app


class TestApp(object):
    def test_app(self, setup_mock_boto3):
        client = boto3.client("ec2")
        output = """\
vpc-03b96307a33428987  cvpn_test_vpc_cvpn  10.0.0.0/16 (10.0.0.1-10.0.255.254) (owner_id: 100000000000)
  [rtb-05abd25320cfd90b9]  <Main route table>
  10.0.0.0/16   local

    subnet-0d4b9e1cf2223169a  cvpn_test_subnet_cvpn  us-west-2a  10.0.1.0/24 (10.0.1.1-10.0.1.254)
      [rtb-0edab5f8845653e29] cvpn_test_rt
      10.0.0.0/16   local
      10.10.0.0/16  vpc_peering: 100000000000|ap-northeast-1|vpc-085071b77f46b90cd|10.10.0.0/16

vpc-04da3256                               172.31.0.0/16 (172.31.0.1-172.31.255.254) (owner_id: 100000000000)
  [rtb-e50a5a34]  <Main route table>
  172.31.0.0/16 local
  0.0.0.0/0     igw-046c054d

    subnet-613079a6                                  us-west-2a  172.31.16.0/20 (172.31.16.1-172.31.31.254)
    subnet-a5d28191                                  us-west-2b  172.31.32.0/20 (172.31.32.1-172.31.47.254)
    subnet-05e9b155                                  us-west-2c  172.31.0.0/20 (172.31.0.1-172.31.15.254)
"""
        assert app(client) == output
