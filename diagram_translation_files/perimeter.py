from prettytable import PrettyTable

class Perimeter:
    
    def __init__(self, id, name):
        self.id = id
        self.name = name[:-1].lower()
        self.zones = []
        self.main_zone = 0
        self.base_vid = 0
    
    def add_base_vid(self, vid):
        self.base_vid = vid 

    def add_zone(self, zone):
        self.zones.append(zone)     

    def print(self): # TODO sistemare il nome
        table = PrettyTable(['id','perimeter', 'zone_id', 'zone', 'node_id', 'node', 'ip'])
        if(len(self.zones) > 0):
            for zone in self.zones:
                for node in zone.nodes:
                    table.add_row([str(self.id), str(self.name).lower(), str(zone.id), str(zone.name).lower(), str(node.id), str(node.name).lower(), str(node.ip)])
        else:
            table.add_row([str(self.name), 'no zones'])
        table.sortby = 'ip'
        return table.get_string()

    def count_nodes(self):
        count = 0
        for zone in self.zones:            
            count += len(zone.nodes)
        return count