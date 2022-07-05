from prettytable import PrettyTable

class Node:
    
    def __init__(self, id, type, zone, name):
        self.id = id
        self.type = type.lower()
        self.zone = zone.lower()
        self.name = name[:-1].lower()
        self.ip = 'L2 (no ip)'
        self.linked = []
        self.switch_port = 0
    
    def assign_type(self):
        if('router' in self.type):
            self.type = 'router'
        elif('switch' in self.type):
            self.type = 'switch'
        elif('cerchio' in self.type or 'circle' in self.type):
            self.type = 'host'
        elif('server' in self.type):
            self.type = 'server'      
    
    def assign_ip(self, ip):
        self.ip = ip
    
    def has_ip (self):
        if(self.ip == 'L2 (no ip)'):
            return False
        else:
            return True

    def add_linked_node(self, id):
        self.linked.append(id)

    def change_switch_port(self, port):
        self.switch_port = port
    
    def print(self):
        table = PrettyTable(['node', 'ip', 'zone'])
        table.add_row([self.name, str(self.ip), str(self.zone)])
        print(table)

        