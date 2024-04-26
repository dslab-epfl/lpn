from lpn_def.pcie_components import PcieSwitch, PcieDevice, PcieUniDirLink
from lpn_def.funcs import *
from lpn_def.all_enum import CstStr

def install_rout(s, list_of_device_int_id, list_of_rout):

    for d, port in zip(list_of_device_int_id, list_of_rout):
        s.install_rout(d, port)

def connect(s1, port1, s2, port2):

    links1s2 = PcieUniDirLink(f"{s1.id}_P2P_{s2.id}")
    links2s1 = PcieUniDirLink(f"{s2.id}_P2P_{s1.id}")

    recv_p_credit = s1.access_node(f"{s1.id}_recvcap_{port1}")
    recv_p = s1.access_node(f"{s1.id}_recv_{port1}")

    links2s1.connect(recv_p)
    s2.connect(port2, recv_p_credit, links2s1)

    recv_p_credit = s2.access_node(f"{s2.id}_recvcap_{port2}") 
    recv_p = s2.access_node(f"{s2.id}_recv_{port2}")

    links1s2.connect(recv_p)
    s1.connect(port1, recv_p_credit, links1s2)

    return links1s2, links2s1

def connect_device(s1, port1, d1):

    links1d1 = PcieUniDirLink(f"{s1.id}_P2P_{d1.id}")
    linkd1s1 = PcieUniDirLink(f"{d1.id}_P2P_{s1.id}")

    recv_p_credit = s1.access_node(f"{s1.id}_recvcap_{port1}")
    recv_p = s1.access_node(f"{s1.id}_recv_{port1}")
    linkd1s1.connect(recv_p)
    d1.connect(recv_p_credit, linkd1s1)

    recv_p_credit = d1.access_node(f"{d1.id}_recvcap") 
    recv_p = d1.access_node(f"{d1.id}_recv")
    links1d1.connect(recv_p)
    s1.connect(port1, recv_p_credit, links1d1)

    return links1d1, linkd1s1
    

def init_topology_1():
    # 0, 1 for downstream
    # 2 for upstream
    # in port buf are named as <id>_recv_<ipt>
    # in port buf credit are named as <id>_recvcap_<ipt>
    # out port transitions are named <id>_send_<opt>

    dual_port_1 = [0, 1, 2]
    switch1 = PcieSwitch("s1", dual_port_1)

    # 3, 4 for downstream
    # 5 for upstream
    dual_port_2 = [3, 4, 5]
    switch2 = PcieSwitch("s2", dual_port_2)

    # 6, 7 for downstream
    # no upstream as this is the root
    dual_port_root = [6, 7]
    root = PcieSwitch("root", dual_port_root, is_rootcomplex=True)

    device1 = PcieDevice("d1")
    device2 = PcieDevice("d2")
    device3 = PcieDevice("d3")
    device4 = PcieDevice("d4")

    # start to connect the switches and root
    recv_p_credit = root.access_node("root_recvcap_6")
    recv_p = root.access_node("root_recv_6")
    switch1.connect(2, recv_p_credit, recv_p)

    recv_p_credit = switch1.access_node("s1_recvcap_2") 
    recv_p = switch1.access_node("s1_recv_2")
    root.connect(6, recv_p_credit, recv_p)
    
    recv_p_credit = root.access_node("root_recvcap_7")
    recv_p = root.access_node("root_recv_7")
    switch2.connect(5, recv_p_credit, recv_p)

    recv_p_credit = switch2.access_node("s2_recvcap_5") 
    recv_p = switch2.access_node("s2_recv_5")
    root.connect(7, recv_p_credit, recv_p)

    # populate rout infomation
    switch1.install_rout(CstStr.D1, 0)
    switch1.install_rout(CstStr.D2, 1)
    switch1.install_rout(CstStr.D3, 2)
    switch1.install_rout(CstStr.D4, 2)

    switch2.install_rout(CstStr.D1, 5)
    switch2.install_rout(CstStr.D2, 5)
    switch2.install_rout(CstStr.D3, 3)
    switch2.install_rout(CstStr.D4, 4)

    root.install_rout(CstStr.D1, 6)
    root.install_rout(CstStr.D2, 6)
    root.install_rout(CstStr.D3, 7)
    root.install_rout(CstStr.D4, 7)

    #connect 4 devices

    recv_p_credit = switch1.access_node("s1_recvcap_0") 
    recv_p = switch1.access_node("s1_recv_0")
    device1.connect(recv_p_credit, recv_p)

    recv_p_credit = switch1.access_node("s1_recvcap_1") 
    recv_p = switch1.access_node("s1_recv_1")
    device2.connect(recv_p_credit, recv_p)


    recv_p_credit = switch2.access_node("s2_recvcap_3") 
    recv_p = switch2.access_node("s2_recv_3")
    device3.connect(recv_p_credit, recv_p)

    recv_p_credit = switch2.access_node("s2_recvcap_4") 
    recv_p = switch2.access_node("s2_recv_4")
    device4.connect(recv_p_credit, recv_p)

    # connect send to device
    recv_p_credit = device1.access_node("d1_recvcap") 
    recv_p = device1.access_node("d1_recv")
    switch1.connect(0, recv_p_credit, recv_p)

    recv_p_credit = device2.access_node("d2_recvcap") 
    recv_p = device2.access_node("d2_recv")
    switch1.connect(1, recv_p_credit, recv_p)

    recv_p_credit = device3.access_node("d3_recvcap") 
    recv_p = device3.access_node("d3_recv")
    switch2.connect(3, recv_p_credit, recv_p)

    recv_p_credit = device4.access_node("d4_recvcap") 
    recv_p = device4.access_node("d4_recv")
    switch2.connect(4, recv_p_credit, recv_p)

    return [switch1, switch2, root, device1, device2, device3, device4]


def init_topology_2():
    # 8 device

    # 0, 1 for downstream
    # 2 for upstream
    # in port buf are named as <id>_recv_<ipt>
    # in port buf credit are named as <id>_recvcap_<ipt>
    # out port transitions are named <id>_send_<opt>

    dual_port_1 = [0, 1, 2]
    switch1 = PcieSwitch("s1", dual_port_1)

    # 3, 4 for downstream
    # 5 for upstream
    dual_port_2 = [3, 4, 5]
    switch2 = PcieSwitch("s2", dual_port_2)

    # 6, 7 for downstream
    # 8 for upstream
    dual_port_3 = [6, 7, 8]
    switch3 = PcieSwitch("s3", dual_port_3)

    # 9, 10 for downstream
    # 11 for upstream
    dual_port_4 = [9, 10, 11]
    switch4 = PcieSwitch("s4", dual_port_4)

    # 12, 13 for downstream
    # 14 for upstream
    dual_port_5 = [12, 13, 14]
    switch5 = PcieSwitch("s5", dual_port_5)

    # 15, 16 for downstream
    # 17 for upstream
    dual_port_6 = [15, 16, 17]
    switch6 = PcieSwitch("s6", dual_port_6)

    # 18, 19 for downstream
    # no upstream as this is the root
    dual_port_root = [18, 19]
    root = PcieSwitch("root", dual_port_root, is_rootcomplex=True)

    device1 = PcieDevice("d1")
    device2 = PcieDevice("d2")
    device3 = PcieDevice("d3")
    device4 = PcieDevice("d4")
    device5 = PcieDevice("d5")
    device6 = PcieDevice("d6")
    device7 = PcieDevice("d7")
    device8 = PcieDevice("d8")

    # start to connect the switches and root
    connect(root, 18, switch5, 14)
    connect(root, 19, switch6, 17)
    connect(switch5, 12, switch1, 2)
    connect(switch5, 13, switch2, 5)
    connect(switch6, 15, switch3, 8)
    connect(switch6, 16, switch4, 11)

    connect_device(switch1, 0, device1)
    connect_device(switch1, 1, device2)
    connect_device(switch2, 3, device3)
    connect_device(switch2, 4, device4)
    connect_device(switch3, 6, device5)
    connect_device(switch3, 7, device6)
    connect_device(switch4, 9, device7)
    connect_device(switch4, 10, device8)

    # populate rout infomation
    list_of_device = [device1,device2,device3,device4,device5,device6,device7,device8]
    list_of_device_int_id = [CstStr.D1, CstStr.D2, CstStr.D3, CstStr.D4, CstStr.D5, CstStr.D6, CstStr.D7, CstStr.D8]
    install_rout(switch1, list_of_device_int_id, [0, 1, 2, 2, 2, 2, 2, 2])
    install_rout(switch2, list_of_device_int_id, [5, 5, 3, 4, 5, 5, 5, 5])
    install_rout(switch3, list_of_device_int_id, [8, 8, 8, 8, 6, 7, 8, 8])
    install_rout(switch4, list_of_device_int_id, [11,11,11,11,11,11,9, 10])
    install_rout(switch5, list_of_device_int_id, [12,12,13,13,14,14,14,14])
    install_rout(switch6, list_of_device_int_id, [17,17,17,17,15,15,16,16])
    install_rout(root,    list_of_device_int_id, [18,18,18,18,19,19,19,19])

    return [switch1, switch2, switch3, switch4, switch5, switch6, root, \
        device1, device2, device3, device4, device5, device6, device7, device8] 



def init_topology_3():
    # 8 device

    # 0, 1 for downstream
    # 2 for upstream
    # in port buf are named as <id>_recv_<ipt>
    # in port buf credit are named as <id>_recvcap_<ipt>
    # out port transitions are named <id>_send_<opt>

    # 18, 19 for downstream
    # no upstream as this is the root
    dual_port_root = [0, 1]
    root = PcieSwitch("root", dual_port_root, is_rootcomplex=True)

    device1 = PcieDevice("d1")
    device2 = PcieDevice("d2")
    
    # start to connect the switches and root

    connect_device(root, 0, device1)
    connect_device(root, 1, device2)

    # populate rout infomation
    list_of_device = [device1,device2]
    list_of_device_int_id = [CstStr.D1, CstStr.D2]
    install_rout(root, list_of_device_int_id, [0, 1])

    return [root, device1, device2] 

def init_topology_with_cpu():
    # 2 device
    # 0, 1 for downstream
    # 2 for upstream
    # in port buf are named as <id>_recv_<ipt>
    # in port buf credit are named as <id>_recvcap_<ipt>
    # out port transitions are named <id>_send_<opt>

    # 18, 19 for downstream
    # no upstream as this is the root
    dual_port_s1 = [0, 5, 6]
    switch1 = PcieSwitch("s1", dual_port_s1)

    dual_port_root = [0, 2]
    root = PcieSwitch("root", dual_port_root, is_rootcomplex=True)

    device1 = PcieDevice("d1")
    device2 = PcieDevice("d2")
    device3 = PcieDevice("d3")
    
    links = []
    # start to connect the switches and root

    l1, l2 = connect_device(switch1, 6, device3)
    links.extend([l1, l2])

    l1, l2 = connect_device(switch1, 5, device1)
    links.extend([l1, l2])
    l1, l2 = connect_device(root, 0, device2)
    links.extend([l1, l2])
    l1, l2 = connect(root, 2, switch1, 0)
    links.extend([l1, l2])

    # populate rout infomation
    list_of_device = [device1, device2, device3]
    list_of_device_int_id = [CstStr.D1, CstStr.D2, CstStr.D3]
    install_rout(switch1, list_of_device_int_id, [5, 0, 6])
    install_rout(root, list_of_device_int_id, [2, 0, 2])

    comp_list = [root, switch1, device1, device2, device3]
    comp_list.extend(links)
    return comp_list