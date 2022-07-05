from prettytable import PrettyTable

class Zone:
    
    def __init__(self, id, perimeter, name):
        self.id = id        
        self.perimeter = perimeter.lower()
        self.name = name[:-1].lower()
        self.nodes = []
        self.links = []
        self.vips = []
        self.vid = 0
        self.mac = 0
        self.linked_perimeters = []

    def add_node(self, node):
        self.nodes.append(node)
    
    def add_vid(self, vid):
        self.vid = vid

    def add_linked_perimeter(self, perimeter):
        self.linked_perimeters.append(perimeter)

    def add_vip(self, vip):
        self.vips.append(str(vip) + '/24')
    
    def add_mac(self, mac):
        self.mac = str(mac)

    def add_linked_zone(self, id):
        if(self.id != id):
            self.links.append(id)
    
    def is_linked_to(self, zone):
        for link in self.links:
            for node in zone.nodes:
                if(link.id_dst == node.id):
                    return True

    def print(self):
        table = PrettyTable(['zone', 'vips', 'macs', 'vid'])
        for vip in self.vips:
            for mac in self.macs:
                table.add_row([self.name, str(vip), str(mac), str(self.vid)])
        table.sortby = 'vips'
        print(table)

    def print_nodes(self):
        table = PrettyTable(['zone', 'node', 'ip'])
        for node in self.nodes:
            table.add_row([self.name, node.name, str(node.ip)])
        table.sortby = 'ip'
        print(table)

    def last_ip(self):
        last_ip = ''
        for node in self.nodes:
            last_ip = node.ip
        return last_ip