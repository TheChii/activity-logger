import time
import logging
from scapy.all import sniff
import psutil
import os
import atexit  

def setup_logger(name, log_file, level=logging.INFO):
    logs_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'logs'))
    os.makedirs(logs_dir, exist_ok=True)
    log_file_path = os.path.join(logs_dir, log_file)
    
    handler = logging.FileHandler(log_file_path)
    handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
    logger = logging.getLogger(name)
    logger.setLevel(level)
    logger.addHandler(handler)
    
    atexit.register(handler.close)
    
    return logger
network_logger = setup_logger('network', 'network.log', level=logging.INFO)
logs_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'logs')
os.makedirs(logs_dir, exist_ok=True) 

def get_process_name_for_connection(ip, port):
    connections = psutil.net_connections(kind='inet')
    for conn in connections:
        if conn.laddr.ip == ip and conn.laddr.port == port:
            try:
                process = psutil.Process(conn.pid)
                return process.name()
            except psutil.NoSuchProcess:
                continue
    return "Unknown"

def monitor_network():
    network_logger.info("Started monitoring network activity")
    
    def packet_callback(packet):
        if packet.haslayer("IP"):
            ip_layer = packet["IP"]
            src_ip = ip_layer.src
            dst_ip = ip_layer.dst
            proto = ip_layer.proto 
            
            protocol_handlers = {
                "TCP": lambda: handle_tcp(src_ip, dst_ip, packet),
                "UDP": lambda: handle_udp(src_ip, dst_ip, packet),
            }
            
            transport_layer = "Unknown"
            if packet.haslayer("TCP"):
                transport_layer = "TCP"
            elif packet.haslayer("UDP"):
                transport_layer = "UDP"
            
            if transport_layer in protocol_handlers:
                protocol_handlers[transport_layer]()
            else:
                network_logger.info(f"Normal packet - Protocol: {proto}, Src: {src_ip}, Dst: {dst_ip}, Transport: {transport_layer}")
        
    
    def handle_tcp(src_ip, dst_ip, packet):
        src_port = packet["TCP"].sport
        dst_port = packet["TCP"].dport
        process_name_src = get_process_name_for_connection(src_ip, src_port)
        process_name_dst = get_process_name_for_connection(dst_ip, dst_port)
        log_message = f"TCP Packet details - Src: {src_ip}:{src_port} ({process_name_src}), Dst: {dst_ip}:{dst_port} ({process_name_dst})"
        log_packet(log_message, src_ip, dst_ip)
    
    def handle_udp(src_ip, dst_ip, packet):
        src_port = packet["UDP"].sport
        dst_port = packet["UDP"].dport
        process_name_src = get_process_name_for_connection(src_ip, src_port)
        process_name_dst = get_process_name_for_connection(dst_ip, dst_port)
        log_message = f"UDP Packet details - Src: {src_ip}:{src_port} ({process_name_src}), Dst: {dst_ip}:{dst_port} ({process_name_dst})"
        log_packet(log_message, src_ip, dst_ip)
    
    def log_packet(message, src_ip, dst_ip):
        if src_ip.startswith("192.168.") and dst_ip not in ["192.168.1.9", "192.168.1.2"]:
            network_logger.warning(f"Suspicious outbound packet detected: {message}")
        elif dst_ip.startswith("192.168.") and src_ip not in ["192.168.1.9", "192.168.1.2"]:
            network_logger.warning(f"Suspicious inbound packet detected: {message}")
        else:
            network_logger.info(f"Normal packet: {message}")
    
    try:
        sniff(prn=packet_callback, store=0)
    except KeyboardInterrupt:
        network_logger.info("Stopped monitoring network activity")
    except Exception as e:
        network_logger.error(f"Error in network monitoring: {e}")

if __name__ == "__main__":
    monitor_network()
