import logging
import socket
import re
import subprocess
import ipaddress
import threading
from src.utils.config import Config

class NetworkSecurity:
    """
    Network security module for controlled network scanning and security operations.
    Provides safe wrappers around networking tools with proper validation.
    """
    
    def __init__(self):
        """Initialize the network security module with safe defaults."""
        # Network scanning limits
        self.max_scan_hosts = Config.get("max_scan_hosts", 256)
        self.max_scan_ports = Config.get("max_scan_ports", 1000)
        self.allowed_scan_ranges = Config.get("allowed_scan_ranges", ["127.0.0.1/32", "192.168.0.0/16", "10.0.0.0/8", "172.16.0.0/12"])
        
        # Default timeouts (seconds)
        self.connect_timeout = Config.get("network_connect_timeout", 2)
        self.scan_timeout = Config.get("network_scan_timeout", 30)
        
        logging.info("Network Security module initialized")
    
    def is_ip_allowed(self, ip):
        """
        Check if an IP address is within allowed scan ranges.
        
        Args:
            ip (str): IP address to check
            
        Returns:
            bool: True if allowed, False otherwise
        """
        try:
            ip_obj = ipaddress.ip_address(ip)
            
            # Check against each allowed range
            for allowed_range in self.allowed_scan_ranges:
                network = ipaddress.ip_network(allowed_range)
                if ip_obj in network:
                    return True
            
            logging.warning(f"IP {ip} is outside allowed scan ranges")
            return False
        except Exception as e:
            logging.error(f"Error checking IP {ip}: {e}")
            return False
    
    def validate_port_range(self, port_range):
        """
        Validate a port range string (e.g., "80", "1-1000").
        
        Args:
            port_range (str): Port range to validate
            
        Returns:
            tuple: (is_valid, port_list or error_message)
        """
        try:
            # Check formats: single port "80" or range "1-1000"
            if re.match(r'^\d+, port_range):
                # Single port
                port = int(port_range)
                if 1 <= port <= 65535:
                    return True, [port]
                else:
                    return False, "Port must be between 1-65535"
            elif re.match(r'^\d+-\d+, port_range):
                # Port range
                start, end = map(int, port_range.split('-'))
                if 1 <= start <= end <= 65535:
                    if end - start > self.max_scan_ports:
                        return False, f"Port range too large. Maximum is {self.max_scan_ports}"
                    return True, list(range(start, end + 1))
                else:
                    return False, "Ports must be between 1-65535 and start must be less than end"
            else:
                return False, "Invalid port format. Use '80' or '1-1000'"
        except Exception as e:
            logging.error(f"Error validating port range {port_range}: {e}")
            return False, f"Invalid port range: {str(e)}"
    
    def validate_ip_range(self, ip_range):
        """
        Validate an IP range (e.g., "192.168.1.1", "192.168.1.0/24").
        
        Args:
            ip_range (str): IP or range to validate
            
        Returns:
            tuple: (is_valid, ip_list or error_message)
        """
        try:
            # Single IP address
            if re.match(r'^\d+\.\d+\.\d+\.\d+, ip_range):
                if self.is_ip_allowed(ip_range):
                    return True, [ip_range]
                else:
                    return False, "IP address not in allowed scan ranges"
            
            # CIDR notation (e.g. 192.168.1.0/24)
            elif re.match(r'^\d+\.\d+\.\d+\.\d+/\d+, ip_range):
                network = ipaddress.ip_network(ip_range, strict=False)
                
                # Check size of network
                host_count = network.num_addresses
                if host_count > self.max_scan_hosts:
                    return False, f"Network too large. Maximum hosts: {self.max_scan_hosts}"
                
                # Convert to list of IPs
                ip_list = [str(ip) for ip in network.hosts()]
                
                # Check if network is allowed
                for allowed_range in self.allowed_scan_ranges:
                    allowed_network = ipaddress.ip_network(allowed_range)
                    if network.subnet_of(allowed_network):
                        return True, ip_list
                
                return False, "Network not in allowed scan ranges"
            
            else:
                return False, "Invalid IP format. Use '192.168.1.1' or '192.168.1.0/24'"
        except Exception as e:
            logging.error(f"Error validating IP range {ip_range}: {e}")
            return False, f"Invalid IP range: {str(e)}"
    
    def safe_port_scan(self, target_ip, ports=None):
        """
        Perform a safe port scan on a target IP.
        
        Args:
            target_ip (str): Target IP address
            ports (list, optional): List of ports to scan
            
        Returns:
            dict: Scan results with open ports
        """
        # Validate IP
        if not self.is_ip_allowed(target_ip):
            return {"error": f"IP {target_ip} is not in allowed scan ranges"}
        
        # Default ports if not specified
        if ports is None:
            ports = [21, 22, 23, 25, 53, 80, 110, 443, 3306, 3389, 8080]
        
        # Limit number of ports
        if len(ports) > self.max_scan_ports:
            ports = ports[:self.max_scan_ports]
        
        results = {
            "target": target_ip,
            "open_ports": [],
            "scanned_ports": len(ports)
        }
        
        logging.info(f"Starting safe port scan on {target_ip}")
        
        try:
            # Set socket timeout
            socket.setdefaulttimeout(self.connect_timeout)
            
            # Track scan start time
            start_time = threading.Event()
            start_time.clear()
            
            # Create a timeout thread
            def timeout_thread():
                start_time.wait(self.scan_timeout)
                if not scan_complete.is_set():
                    logging.warning(f"Port scan on {target_ip} timed out")
            
            scan_complete = threading.Event()
            scan_complete.clear()
            
            timeout_thread = threading.Thread(target=timeout_thread)
            timeout_thread.daemon = True
            timeout_thread.start()
            
            # Start scanning
            start_time.set()
            
            for port in ports:
                try:
                    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    s.settimeout(self.connect_timeout)
                    result = s.connect_ex((target_ip, port))
                    if result == 0:
                        # Port is open
                        service = self._get_service_name(port)
                        results["open_ports"].append({
                            "port": port,
                            "service": service
                        })
                    s.close()
                except:
                    pass
            
            scan_complete.set()
            
            logging.info(f"Port scan completed on {target_ip}. Found {len(results['open_ports'])} open ports")
            return results
            
        except Exception as e:
            logging.error(f"Error during port scan on {target_ip}: {e}")
            return {"error": f"Port scan failed: {str(e)}"}
    
    def safe_ping(self, target_ip):
        """
        Safely ping a target IP address.
        
        Args:
            target_ip (str): Target IP to ping
            
        Returns:
            dict: Ping results
        """
        # Validate IP
        if not self.is_ip_allowed(target_ip):
            return {"error": f"IP {target_ip} is not in allowed scan ranges"}
        
        logging.info(f"Pinging {target_ip}")
        
        try:
            # Construct safe ping command with timeout
            if os.name == 'nt':  # Windows
                command = f"ping -n 1 -w 1000 {target_ip}"
            else:  # Linux/Mac
                command = f"ping -c 1 -W 1 {target_ip}"
            
            # Execute ping
            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=2  # Overall timeout
            )
            
            # Parse result
            if result.returncode == 0:
                # Extract response time if available
                time_match = re.search(r'time=(\d+(\.\d+)?)', result.stdout)
                response_time = float(time_match.group(1)) if time_match else None
                
                return {
                    "target": target_ip,
                    "status": "alive",
                    "response_time_ms": response_time
                }
            else:
                return {
                    "target": target_ip,
                    "status": "unreachable"
                }
                
        except subprocess.TimeoutExpired:
            logging.warning(f"Ping to {target_ip} timed out")
            return {"target": target_ip, "status": "timeout"}
            
        except Exception as e:
            logging.error(f"Error pinging {target_ip}: {e}")
            return {"error": f"Ping failed: {str(e)}"}
    
    def ping_sweep(self, subnet):
        """
        Perform a ping sweep on a subnet.
        
        Args:
            subnet (str): Subnet in CIDR notation (e.g., "192.168.1.0/24")
            
        Returns:
            list: List of live hosts
        """
        # Validate subnet
        is_valid, ip_list_or_error = self.validate_ip_range(subnet)
        
        if not is_valid:
            return {"error": ip_list_or_error}
        
        ip_list = ip_list_or_error
        
        live_hosts = []
        
        logging.info(f"Starting ping sweep on {subnet}")
        
        # Use threadpool for parallel execution
        from concurrent.futures import ThreadPoolExecutor
        with ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(self.safe_ping, ip) for ip in ip_list]
            for future in futures:
                result = future.result()
                if "status" in result and result["status"] == "alive":
                    live_hosts.append(result["target"])
        
        logging.info(f"Ping sweep completed on {subnet}. Found {len(live_hosts)} live hosts")
        
        return {
            "subnet": subnet,
            "hosts_scanned": len(ip_list),
            "live_hosts": live_hosts,
            "live_host_count": len(live_hosts)
        }
    
    def _get_service_name(self, port):
        """
        Get the service name for a port number.
        
        Args:
            port (int): Port number
            
        Returns:
            str: Service name or "unknown"
        """
        common_ports = {
            21: "FTP",
            22: "SSH",
            23: "Telnet",
            25: "SMTP",
            53: "DNS",
            80: "HTTP",
            110: "POP3",
            143: "IMAP",
            443: "HTTPS",
            3306: "MySQL",
            3389: "RDP",
            5432: "PostgreSQL",
            8080: "HTTP-Alt"
        }
        
        return common_ports.get(port, "unknown")