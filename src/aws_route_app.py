from aws_resources import VPCs, Subnets, VpcPeeringConnection, RouteTables


def app(client):
    vpcs = VPCs(client)
    subnets = Subnets(client)
    peering_connections = VpcPeeringConnection(client)
    route_tables = RouteTables(client, peering_connections)

    output = ""

    for vpc in vpcs:
        main_route_table = route_tables.find_route_table_main(vpc.VpcId)

        output += str(vpc) + "\n"
        output += str(main_route_table) + "\n"

        for subnet in subnets.find_by_vpc_id(vpc.VpcId):
            sub_route_tables = route_tables.find_route_tables_sub(
                vpc.VpcId, subnet.SubnetId
            )

            output += str(subnet) + "\n"
            for sub_route_table in sub_route_tables:
                output += str(sub_route_table) + "\n"

    return output
