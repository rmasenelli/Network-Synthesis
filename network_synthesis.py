from diagram_translation_files.node import Node
from diagram_translation_files.link import Link
from diagram_translation_files.zone import Zone
from diagram_translation_files.perimeter import Perimeter
from tkinter import Tk
from tkinter.filedialog import askopenfilename
from operator import getitem
import os
import subprocess
import yaml
import glob
import time

# ----------- FUNZIONI -----------

def cleanup(): # pulisce le vecchie configurazioni, file e namespace
    subprocess.call(['/bin/bash', '-i', '-c', 'cleanup'])    
    files = glob.glob("outputs/*")
    for file in files:
        os.remove(file)

def create_objects(): # parsing del file e creazione degli oggetti
    for line in lines:
        raw = line.split(',')
        if(raw[1] == 'Linea' or raw[1] == 'Line'):
            link = Link(raw[0], raw[6], raw[7], raw[11])
            links.append(link)
        elif(raw[1] == 'Zona' or raw[1] == 'Zone'):
            if(raw[4] == ''):
                print('ERROR: zone ' + raw[0] + ' not in a perimeter!')
                exit(-1)
            zone = Zone(raw[0], raw[4], raw[11])
            zones.append(zone)
        elif(raw[1] == 'Regione' or raw[1] == 'Region'):
            perimeter = Perimeter(raw[0], raw[11])
            perimeters.append(perimeter)
        else:
            if('|' in raw[4]):
                zone = raw[4].split('|')
                if(len(raw[11]) > 11):
                    print('ERROR: node ' + raw[0] + ' name too long! max 11 char')
                    exit(-1)
                node = Node(raw[0], raw[1], zone[1], raw[11])
            else:        
                print('ERROR: node ' + raw[0] + ' not in a zone!')
                exit(-1)
            node.assign_type()
            nodes.append(node)

def populate_zones(): # aggiunta dei nodi alle zone
    for zone in zones:
        for node in nodes:
            if(node.zone == zone.id):
                zone.add_node(node)

def populate_perimeters(): # aggiunta delle zone ai perimetri
    for perimeter in perimeters:
        for zone in zones:
            if(perimeter.id == zone.perimeter):
                perimeter.add_zone(zone)

def find_links(): # ricerca di tutti i collegamenti
    for node in nodes: # (nodo corrente)
        for link in links:
            if(link.id_src == node.id): # nodo corrente (partenza)
                node.add_linked_node(link.id_dst) # viene aggiunto alla lista dei link il nodo destinazione
                zone1 = get_zone(node.zone) # zona del nodo corrente
                check = get_node(link.id_dst)
                if(check == -1):
                    print('ERROR: check ' + node.name + ' source link!\n')
                    exit(-1)
                else:
                    zone2 = get_zone(check.zone) # zona del nodo destinazione
                # se il link non esiste ancora nella lista della zona viene aggiunto
                if(zone2.id not in zone1.links): 
                    zone1.add_linked_zone(zone2.id) 
                if(zone1.id not in zone2.links):
                    zone2.add_linked_zone(zone1.id) 
                perimeter1 = get_perimeter(zone1.perimeter) # perimetro del nodo di partenza (corrente) 
                perimeter2 = get_perimeter(zone2.perimeter) # perimetro del nodo di destinazione
                # se il collegamento tra i zona e perimetro non esiste viene aggiunto ad entrambe le zone                   
                if(perimeter1.id != perimeter2.id and (perimeter1 not in zone2.linked_perimeters and perimeter2 not in zone1.linked_perimeters)): 
                    zone1.add_linked_perimeter(perimeter2)
                    zone2.add_linked_perimeter(perimeter1)
            elif(link.id_dst == node.id): # nodo corrente (destinazione)
                node.add_linked_node(link.id_src)
                zone1 = get_zone(node.zone)
                check = get_node(link.id_src)
                if(check == -1):
                    print('ERROR: check ' + node.name + ' destination link!\n')
                    exit(-1)
                else:
                    zone2 = get_zone(check.zone)
                if(zone2.id not in zone1.links):
                    zone1.add_linked_zone(zone2.id)
                if(zone1.id not in zone2.links):
                    zone2.add_linked_zone(zone1.id)
                perimeter1 = get_perimeter(zone1.perimeter)
                perimeter2 = get_perimeter(zone2.perimeter)
                if(perimeter1.id != perimeter2.id and (perimeter1 not in zone2.linked_perimeters and perimeter2 not in zone1.linked_perimeters)):
                    zone1.add_linked_perimeter(perimeter2)
                    zone2.add_linked_perimeter(perimeter1)
            elif(link.id_dst == '' or link.id_src == ''):
                print('ERROR: link ' + link.id + ' is unconnected!')
                exit(0)

def get_perimeter(id): # ritorna il perimetro in base all'id
    for perimeter in perimeters:
        if(perimeter.id == id):
            return perimeter
    return -1

def get_node(id): # ritorna il nodo in base all'id 
    for node in nodes:
        if(node.id == id):
            return node
    return -1

def get_zone(id): # ritorna la zona in base all'id 
    for zone in zones:
        if(int(zone.id) == int(id)):
            return zone
    return -1  

def translate_ip(ip): # traduce l'ip da lista in stringa
    return '.'.join([str(num) for num in ip])

def save_network_configuration(): # salva la configurazione della rete su file
    for perimeter in perimeters:
        file = open('outputs/network.log', 'a', encoding = 'utf8')
        file.write(perimeter.print() + '\n')

def create_mac(ip): # traduce l'ip per creare il mac
    mac = ''
    for i in range(12-len(str(ip))):
        mac += '0'
    mac += str(ip)
    mac = ':'.join(mac[i:i+2] for i in range(0,12,2))
    return mac

def find_main_zones(): # trova le zone principali di ogni perimetro
    for perimeter in perimeters:
        size = 0
        for zone in perimeter.zones:
            if(len(zone.links) > size):
                size = len(zone.links)
                perimeter.main_zone = zone # viene aggiunta al perimetro
    for perimeter in perimeters:
        main_zones.append(perimeter.main_zone) # lista di tutte le zone principali del diagramma

def find_super_zone(): # trova la zona principale di tutto il diagramma
    size_z = 0 # dimensione dei perimetri collegati
    size_n = 0 # dimensioni dei nodi all'interno
    for zone in main_zones:
        if(size_z < len(zone.linked_perimeters)): # la zona con piu perimetri            
            size_z = len(zone.linked_perimeters)
            size_n = len(zone.nodes)
            super_zone = zone
        elif(size_z == len(zone.linked_perimeters)): # se n perimetri == allora controlla il numeri di nodi
            if(size_n < len(zone.nodes)):
                size_z = len(zone.linked_perimeters)
                size_n = len(zone.nodes)
                super_zone = zone
    return super_zone

def create_host(node): # crea gli host con namespace e ip 
    cmd = 'create_ns ' + node.name + ' ' + node.ip + '/24'
    subprocess.call(['/bin/bash', '-i', '-c', cmd])

'''def assign_gateway(node): # assegna il gateway al nodo
    gateway = (node.ip).split('.') # lo divido nei 4 byte
    gateway = list(map(int, gateway))
    gateway[3] = str(254)
    gateway = '.'.join([str(num) for num in gateway])
    cmd = 'as_ns ' + node.name + ' ip route add default via ' + gateway + ' dev veth0'
    subprocess.call(['/bin/bash', '-i', '-c', cmd])'''

def add_tagged_interface(): # aggiunta delle tagged interface ai nodi delle main zones 
    for perimeter in perimeters:
        for node in perimeter.main_zone.nodes:
            if('switch' != node.type):
                for link in perimeter.main_zone.links:
                    zone = get_zone(link)
                    ip = zone.last_ip() # ultimo ip utilizzato nella zona
                    ip = ip.split('.')
                    ip = list(map(int, ip))
                    new_ip = [0,0,0,0]
                    for tmp_ip in used_ips:
                        tmp_ip = tmp_ip.split('.')
                        tmp_ip = list(map(int, tmp_ip))
                        if(tmp_ip[2] == ip[2]):
                            if(tmp_ip[3] > new_ip[3] and tmp_ip[3] != 254):
                                new_ip = tmp_ip
                    new_ip[3] += 1
                    used_ips.append(translate_ip(new_ip))
                    if(not(perimeter.main_zone.id != super_zone.id and zone.vid == super_zone.vid)):
                        cmd = 'add_tagged_interface ' + node.name + ' ' + str(zone.vid) + ' ' + translate_ip(new_ip) + '/24' # creazione della tagged interface
                        subprocess.call(['/bin/bash', '-i', '-c', cmd])
                        cmd = 'as_ns ' + node.name + ' ip address add ' + node.ip + '/24 dev veth0' # assegnamento dell'ip ad ogni nodo con una tagged interface (per la comunicazione interna alla vlan) 
                        subprocess.call(['/bin/bash', '-i', '-c', cmd])

def from_ids_to_vids(links): # data una lista di id ne restituisce i vid in relazione all'id
    vids = []
    for link in links:
        zone = get_zone(link)
        if(zone != super_zone and zone.vid != super_zone.vid):
            vids.append(zone.vid)
    return vids

def ping1(): # ping attraverso la funzione bash as_ns gli host all'interno della stessa zona
    for zone in zones:
        if(len(zone.nodes) > 1):
            for node1 in zone.nodes[:1]:
                for node2 in zone.nodes[1:]:
                    if(node1.id != node2.id):
                        if('switch' not in node1.type and 'switch' not in node2.type):
                            #print(node1.name + ' (' + node1.ip + ') ping ' + node2.name + ' (' + node2.ip + ')')
                            cmd = 'as_ns ' + node1.name + ' ping -c 2 -q ' + node2.ip + '>> outputs/ping1.log'
                            subprocess.call(['/bin/bash', '-i', '-c', cmd])

def ping2(): # ping attraverso la funzione bash as_ns le zone linkate alla central zone
    for zone in main_zones:
        for node1 in super_zone.nodes:
            if(zone.id in super_zone.links):
                for node2 in zone.nodes:
                    if(node1.id != node2.id):
                        if('switch' not in node1.type and 'switch' not in node2.type):
                            #print(node1.name + ' (' + node1.ip + ') ping ' + node2.name + ' (' + node2.ip + ')')
                            cmd = 'as_ns ' + node1.name + ' ping -c 2 -q ' + node2.ip + '>> outputs/ping2.log'
                            subprocess.call(['/bin/bash', '-i', '-c', cmd])

def check_sudo(): # controlla che lo script sia eseguito come root
    if os.geteuid() != 0:
        print("0. eseguire questo script come root (sudo python3 network_synthesis.py)")
        exit(-1)

# ----------- INIZIO CODICE -----------

check_sudo() # controllo esecuzione come root
print('1. pulizia in corso...')
cleanup() # eliminazione file, namespace e configurazioni presenti
print('\tcompletato.\n')

fillet = '-----------------------------------------------------------------------------'

nodes      = [] # lista dei nodi
links      = [] # lista dei collegamenti
zones      = [] # lista delle zone
perimeters = [] # lista dei perimetri
main_zones = [] # lista delle main zones

# ----------- LETTURA DEL DIAGRAMMA DI RETE -----------

Tk().withdraw() 
filename    = askopenfilename() # richiesta del file csv
start_time  = time.time() # inizio conteggio del tempo di esecuzione
file        = open(filename, 'r', encoding = 'utf-8') # lettura dello schema della rete
lines       = file.readlines()[3:] # le prime 3 righe vanno scartate

# ----------- CREAZIONE DEI NODI, ZONE, PERIMETRI -----------

print('2. creazione degli oggetti in corso...')

create_objects() # creazione degli oggetti
populate_zones() # popolamento delle zone 
populate_perimeters() # popolamento dei perimetri

# ----------- RICERCA DEI COLLEGAMENTI -----------

print('\tcompletato.\n\n3. cercando collegamenti...')

find_links() # ricerca dei collegamenti di tutto il diagramma
find_main_zones() # ricerca della zona principale di ogni perimetro
super_zone = find_super_zone() # ricerca della zona centrale di tutta la rete (quella collegata al maggior numero di perimetri)

print('\tcompletato. zona centrale trovata: '+ super_zone.name + '\n')

ip = '10.0.1.1' # ip di partenza
ip = ip.split('.')
ip = list(map(int, ip)) # string --> int []
used_ips  = [] # lista di ip 
used_vids = [] # lista dei vid 
used_macs = [] # lista dei mac

# ----------- ASSEGNAMENTO DEGLI IP, VID e MAC ALLE ZONE e ai NODI -----------

print('4. assegnamento degli ip, vid e mac alle zone in corso...')

for perimeter in perimeters:
    for zone in perimeter.zones:
        if(zone.id == perimeter.main_zone.id): # partenza dalla main zone di ogni perimetro
            ip[3] = 254 # ultimo indirizzo delle zone prima del broadcast
            zone.add_vip(translate_ip(ip)) # aggiunta del vip alla zona per il routing
            used_ips.append(translate_ip(ip))
            zone.add_vid(ip[2] * 100) # le main zones devono avere il vid come multiplo di 100 (100, 200, ...)
            perimeter.add_base_vid(ip[2] * 100)
            used_vids.append(ip[2] * 100)
            zone.add_mac(create_mac(ip[2])) # aggiunta mac alla zona
            used_macs.append(create_mac(ip[2]))  
            ip[3] = 1
            for node in zone.nodes: # assegnamento degli ip agli host della main zone
                if(node.type != 'switch'): # L2
                    node.assign_ip(translate_ip(ip))
                    create_host(node) 
                    used_ips.append(translate_ip(ip))
                    ip[3] += 1 # incremento per altro host
            ip[2] += 1 # cambio di zona

for perimeter in perimeters:
    for zone in perimeter.zones:
        if(zone.id != perimeter.main_zone.id): # assegnamento indirizzi alle non main zones
            ip[3] = 254
            zone.add_vip(translate_ip(ip))
            used_ips.append(translate_ip(ip))
            perimeter.base_vid += 1
            zone.add_vid(perimeter.base_vid)
            used_vids.append(perimeter.base_vid)
            zone.add_mac(create_mac(ip[2]))
            used_macs.append(create_mac(ip[2]))
            ip[3] = 1
            for node in zone.nodes:
                if(node.type != 'switch'):
                    node.assign_ip(translate_ip(ip))
                    create_host(node)
                    used_ips.append(translate_ip(ip))
                    ip[3] += 1
            ip[2] += 1

# ----------- CREAZIONE DELLA CONFIGURAZIONE IN YAML -----------

print('\tcompletato.\n\n5. scrittura del file faucet.yaml in corso... >> /etc/faucet/faucet.yaml')

vlan = dict() # vlan da scrivere in yaml

for perimeter in perimeters:
    for zone in perimeter.zones:
        vlan_name = zone.name
        vlan[vlan_name] = dict()
        vlan[vlan_name]['vid'] = zone.vid         
        vlan[vlan_name]['faucet_vips'] = zone.vips
        vlan[vlan_name]['faucet_mac'] = zone.mac

vlan = dict(sorted(vlan.items(), key = lambda x: getitem(x[1], 'vid'))) # ordinamento delle vlan in base al vid

dps = dict() # datapath da scrivere in yaml

dp_id = 1
switch_name = 'sw1'
dps[switch_name] = dict()
dps[switch_name]['dp_id'] = dp_id
dps[switch_name]['hardware'] = 'Open vSwitch'
dps[switch_name]['interfaces'] = dict()
host_number = 1

for perimeter in perimeters:
    for zone in perimeter.zones:
        if(zone.id == perimeter.main_zone.id): # main zones        
            for node in zone.nodes:
                if('switch' != node.type):
                    str_num = str(host_number)
                    node.change_switch_port(host_number) # assegnamento alla porta dello switch
                    dps[switch_name]['interfaces'][host_number] = dict()
                    dps[switch_name]['interfaces'][host_number]['name'] = node.name          
                    dps[switch_name]['interfaces'][host_number]['native_vlan'] = zone.vid  
                    vids = from_ids_to_vids(zone.links)
                    if(len(vids) > 0): # il nodo è collegato ad altri
                        dps[switch_name]['interfaces'][host_number]['tagged_vlans'] = vids # configurazione delle tagged vlans
                    host_number += 1
        else: # non main zones  
            for node in zone.nodes:
                if('switch' != node.type):
                    str_num = str(host_number)
                    node.change_switch_port(host_number)
                    dps[switch_name]['interfaces'][host_number] = dict()
                    dps[switch_name]['interfaces'][host_number]['name'] = node.name          
                    dps[switch_name]['interfaces'][host_number]['native_vlan'] = zone.vid
                    host_number += 1

network = dict() # unione dei due dizionari per creare il file di configurazione yaml
network['vlans'] = vlan
network['dps'] = dps

with open('/etc/faucet/faucet.yaml', 'w') as outfile:
    yaml.dump(network, outfile, default_flow_style=False, sort_keys=False, indent=4) # creazione del file faucet.yaml per la configurazione di faucet

# ----------- CONTROLLO DEL FILE DI CONFIGURAZIONE -----------

print('\tcompletato.\n\n6. controllo configurazione faucet.yaml in corso...')

os.system('check_faucet_config /etc/faucet/faucet.yaml > outputs/config.log') # comando per verificare il file yaml
faucet_config = open('outputs/config.log', 'r', encoding = 'utf-8')
lines = faucet_config.readlines() # controllo del file appena creato

if(len(lines) == 1): # --> errore
    print('\tERRORE nel file di configurazione faucet.yaml --> ' + lines[0]) # l'errore viene stampato
    exit(-1)

print('\tcompletato.\n\n7. aggiunta delle tagged interface in corso...')

# ----------- AGGIUNTA DELLE TAGGED INTERFACE -----------

add_tagged_interface() # assegnamento delle interfacce ai nodi che sono taggati alle vlan

print('\tcompletato.\n\n8. creazione del datapath in corso...')

# ----------- CREAZIONE DEL DATAPATH -----------

cmd1 = '''sudo ovs-vsctl add-br br0 \\
    -- set bridge br0 other-config:datapath-id=0000000000000001 \\
    -- set bridge br0 other-config:disable-in-band=true \\
    -- set bridge br0 fail_mode=secure \\\n'''

cmd2 = ''

for node in nodes:
    if(node.has_ip() == True): # aggiunta di una porta per ogni host con IP
        cmd2 += '    -- add-port br0 veth-' + node.name + ' -- set interface veth-' + node.name + ' ofport_request=' + str(node.switch_port) + ' \\\n'

cmd3 = '    -- set-controller br0 tcp:127.0.0.1:6653 tcp:127.0.0.1:6654'

# il comando di creazione del datapath è formato da due parti statiche (1 e 3) e da una parte dipendente dall'implementazione della rete (2)
ovs_cmd = cmd1 + cmd2 + cmd3 
os.system(ovs_cmd)

# ----------- RELOADING DI FAUCET -----------

print('\tcompleato.\n\n9. reloading della configurazione di faucet in corso...')

os.system('sudo systemctl reload faucet') # realoading della config di faucet

print('\tcompletato.\n')

# ----------- STAMPA DELLE STATISTICHE -----------

ex_time = time.time() - start_time # execution time
formatted_string = "{:.2f}".format(ex_time)
float_value = float(formatted_string)

print(fillet + '\n\t%s secondi per la creazione %s nodi, %s zone e %s perimetri.\n' % (float_value, len(nodes), len(zones), len(perimeters)) + fillet + '\n')

# ----------- SALVATAGGIO DELL'ASSOCIAZIONE NAMESPACE IP -----------

print('10.salvataggio del file con namespace e ip in corso...')
save_network_configuration()

# ----------- FASE DI TESTING -----------

print('\tcompletato.\n\n11. test con ping in corso... >> outputs/ping.log')

ping1() # ping all'interno della stessa vlan
ping2() # ping tra le vlan linkate

print('\tcompletato.\n')