#
# plural class:
# * query AWS resources
# * find column widths for print
# * create additional fields in the singular class
#
# The role of singular class:
# * child of dict
# * calculate string for print
#
import ipaddress

from json_object import JsonObject


class AWSResource:
    @staticmethod
    def _get_name(resource):
        """find out Name from Tags"""
        tags = resource.get("Tags", [])
        name_tag = next((item for item in tags if item["Key"] == "Name"), {})

        return name_tag.get("Value", "")

    @staticmethod
    def _cidr_str(cidr):
        """convert cider -> cidr (min host ip - max host ip)"""
        network = ipaddress.ip_network(cidr)
        ip_list = list(network)

        # edges excluded for Network and Broadcast (c.f. ipcalc command)
        host_min = ip_list[0] + 1
        host_max = ip_list[-1] - 1

        return "%s (%s-%s)" % (cidr, host_min, host_max)


################################################################################


class VPCs(AWSResource):
    def __init__(self, client):
        super().__init__()
        response = client.describe_vpcs()
        vpcs = JsonObject(response["Vpcs"])
        widths = [0, 0, 0, 0]

        for vpc in vpcs:
            vpc.Name = self._get_name(vpc)
            vpc.CidrStr = self._cidr_str(vpc.CidrBlock)

            widths[0] = max(widths[0], len(vpc.VpcId))
            widths[1] = max(widths[1], len(vpc.Name))
            widths[2] = max(widths[2], len(vpc.CidrStr))
            widths[2] = max(widths[3], len(vpc.OwnerId))

        self.vpcs = [VPC(vpc, widths=widths) for vpc in vpcs]

    def __getitem__(self, item):
        return self.vpcs[item]

    def __iter__(self):
        return self.vpcs.__iter__()


class VPC(dict):
    # to resolve Unresolved attribute reference warnings
    VpcId, Name, CidrStr, OwnerId = 4 * [None]
    widths = 4 * [None]

    # see https://stackoverflow.com/questions/16237659
    def __init__(self, *a, **k):
        super(VPC, self).__init__(*a, **k)
        self.__dict__ = self

    def __str__(self):
        id_, name_, cidr_, owner_ = self.widths
        items = (
            id_,
            self.VpcId,
            name_,
            self.Name,
            cidr_,
            self.CidrStr,
            owner_,
            self.OwnerId,
        )
        return "%-*s  %-*s  %-*s (owner_id: %-*s)" % items


################################################################################


class Subnets(AWSResource):
    def __init__(self, client):
        super().__init__()
        response = client.describe_subnets()
        subnets = JsonObject(response["Subnets"])
        subnets = sorted(subnets, key=lambda e: (e.AvailabilityZone, e.CidrBlock))
        widths = [0, 0, 0, 0]

        for subnet in subnets:
            subnet.Name = self._get_name(subnet)
            subnet.CidrStr = self._cidr_str(subnet.CidrBlock)

            widths[0] = max(widths[0], len(subnet.SubnetId))
            widths[1] = max(widths[1], len(subnet.Name))
            widths[2] = max(widths[2], len(subnet.AvailabilityZone))
            widths[3] = max(widths[3], len(subnet.CidrBlock))

        self.obj = [Subnet(subnet, widths=widths) for subnet in subnets]

    def find_by_vpc_id(self, vpc_id):
        return [subnet for subnet in self.obj if subnet.VpcId == vpc_id]

    def __getitem__(self, item):
        return self.obj[item]

    def __iter__(self):
        return self.obj.__iter__()


class Subnet(dict):
    # to resolve Unresolved attribute reference warnings
    SubnetId, Name, AvailabilityZone, CidrStr, VpcId = 5 * [None]
    widths = 4 * [None]

    def __init__(self, *a, **k):
        super(Subnet, self).__init__(*a, **k)
        self.__dict__ = self

    def __str__(self):
        id_, name_, az_, cidr_ = self.widths
        items = (
            id_,
            self.SubnetId,
            name_,
            self.Name,
            az_,
            self.AvailabilityZone,
            cidr_,
            self.CidrStr,
        )

        return "    %-*s  %-*s  %-*s  %-*s" % items


################################################################################


class RouteTables(AWSResource):
    def __init__(self, client, pcx):
        super().__init__()
        response = client.describe_route_tables()
        route_tables = JsonObject(response["RouteTables"])
        self.pcx = pcx
        widths = [0]

        self.route_tables = [
            RouteTable(rt, pcx=pcx, widths=widths) for rt in route_tables
        ]

        for route_table in self.route_tables:
            route_table.Name = self._get_name(route_table)

            for route in route_table.Routes:
                widths[0] = max(widths[0], len(route.destination))

    def __getitem__(self, item):
        return self.route_tables[item]

    def find_route_table_main(self, vpc_id):
        for route_table in self.route_tables:
            if route_table.VpcId == vpc_id and route_table.is_main:
                return route_table

    def find_route_tables_sub(self, vpc_id, subnet_id):
        route_tables = []

        for route_table in self.route_tables:
            if route_table.VpcId == vpc_id and route_table.is_associate(subnet_id):
                route_tables.append(route_table)

        return route_tables


class RouteTable(dict):
    # to resolve Unresolved attribute reference warnings
    RouteTableId, Name, VpcId, pcx = 4 * [None]
    Routes = []
    Associations = []
    widths = 1 * [None]

    def __init__(self, *a, **k):
        super(RouteTable, self).__init__(*a, **k)
        self.__dict__ = self
        self.is_main = self.Associations[0].Main

        for route in self.Routes:
            route.destination = route.DestinationCidrBlock
            route.target = self._find_route_target(route)

    def _find_route_target(self, route):
        if "VpcPeeringConnectionId" in route:
            return self.pcx.find_peer_vpc(route.VpcPeeringConnectionId, self.VpcId)

        return route.get("GatewayId", route.get("NatGatewayId", "?"))

    def is_associate(self, subnet_id):
        for assoc in self.Associations:
            if assoc.get("SubnetId") == subnet_id:
                return True
        return False

    def __str__(self):
        indent = 2 if self.is_main else 6
        label = " <Main route table>" if self.is_main else ""

        ret = (indent * " ") + "[%s] %s%s\n" % (self.RouteTableId, self.Name, label)

        for route in self.Routes:
            dst_ = self.widths[0]
            items = (indent, " ", dst_, route.destination, route.target)
            ret += "%*s%-*s %-s\n" % items

        return ret


################################################################################


class VpcPeeringConnection:
    def __init__(self, client):
        response = client.describe_vpc_peering_connections()
        self.connections = JsonObject(response["VpcPeeringConnections"])
        self.connections_dict = {
            elm.VpcPeeringConnectionId: elm for elm in self.connections
        }

    def find_peer_vpc(self, vpc_peering_connection_id, vpc_id):
        pcx = self.connections_dict.get(vpc_peering_connection_id)

        if pcx.AccepterVpcInfo.VpcId == vpc_id:
            peer = pcx.RequesterVpcInfo
        else:
            peer = pcx.AccepterVpcInfo

        items = (peer.OwnerId, peer.Region, peer.VpcId, peer.CidrBlock)

        return "vpc_peering: %s|%s|%s|%s" % items

    def __getitem__(self, item):
        return self.connections[item]
