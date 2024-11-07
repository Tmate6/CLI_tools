import requests
import concurrent.futures
import socket
import typer
from typing import Optional
from typing_extensions import Annotated
from rich.progress import track
from rich.table import Table
from rich import print

class IpScanner:
    def __init__(self, baseIp, timeout, portScan):
        self.baseIp = baseIp
        self.timeout = timeout
        self.portScan = portScan
        self.ips = {}
        self.commonPorts = [21, 22, 23, 25, 53, 80, 110, 143, 443, 465, 587, 993, 995, 3306, 3389, 5900, 8080]
        self.responsiveIps = {}

    def getPortInfo(self, port):
        try:
            service = socket.getservbyport(port)
        except OSError:
            service = "Unknown"

        return service

    def scanIp(self, i):
        ip = f"{self.baseIp}{i}"
        try:
            r = requests.get(f"http://{ip}", timeout=self.timeout)
            self.ips[ip] = {'status': r.status_code, 'open_ports': []}

        except requests.RequestException:
            self.ips[ip] = {'status': -1, 'open_ports': []}

    def scanPorts(self, ip):
        for port in self.commonPorts:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(0.5)
            result = sock.connect_ex((ip, port))
            if result == 0:
                self.ips[ip]['open_ports'].append(port)
            sock.close()

    def scanSinglePort(self, args):
        ip, port = args
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(0.1)
        result = sock.connect_ex((ip, port))
        sock.close()
        return port if result == 0 else None

    def fullPortScan(self, ip):
        open_ports = []
        with concurrent.futures.ThreadPoolExecutor(max_workers=100) as executor:
            ports = range(1, 65536)
            results = list(track(executor.map(self.scanSinglePort, [(ip, port) for port in ports]), 
                                total=len(ports), description=f"Scanning ports on {ip}"))

        open_ports = [port for port in results if port is not None]
        return open_ports

    def scan(self):
        with concurrent.futures.ThreadPoolExecutor() as executor:
            list(track(executor.map(self.scanIp, range(1, 255)), total=254, description="Scanning IPs"))

        self.responsiveIps = [ip for ip, data in self.ips.items() if data['status'] != -1]

        if self.portScan:
            with concurrent.futures.ThreadPoolExecutor() as executor:
                list(track(executor.map(self.scanPorts, self.responsiveIps), total=len(self.responsiveIps), description="Scanning Ports"))

    def printFullScanResults(self, ip, open_ports):
        table = Table("Port", "Service")

        for port in open_ports:
            service = self.getPortInfo(port)
            table.add_row(port, service)

        print(table)
        print(f"\nTotal: [[red]{len(open_ports)}[/red]]")

    def printSummary(self):
        if len(self.responsiveIps) == 0:
            print("\n[red]No responsive IPs found.[/red]")
            return
        
        table = Table("#", "IP", "URL", "Open Ports")
        
        responsiveIps = {ip: data for ip, data in self.ips.items() if data['status'] != -1}
        
        for i, (ip, data) in enumerate(responsiveIps.items(), 1):
            url = f"http://{ip}"
            open_ports = ', '.join(str(port) for port in data['open_ports']) if data['open_ports'] else 'None'
            table.add_row(str(i), str(ip), str(url), str(open_ports))

        print()
        print(table)
        print(f"\nTotal: [[red]{len(responsiveIps)}[/red]]")


def main(
        base: Annotated[str, typer.Argument(help="Base ip to iterate over")] = "192.168.0.",
        full: Annotated[Optional[str], typer.Option(help="Fully scan an ip on all ports - give IP")] = None,
        timeout: Annotated[float, typer.Option(help="Timeout for scanning (s)")] = 2,
        portscan: Annotated[bool, typer.Option(help="Perform scans on the most common ports on found ips")] = True):
    
    print("\n[ [bold][red]IP[/red] Scanner[/bold] ]\n")

    ipScanner = IpScanner(base, timeout, portscan)

    if full:
        print(f"Scanning [[red not bold]{full}[/red not bold]] for all ports\n")

        open_ports = ipScanner.fullPortScan(full)
        ipScanner.printFullScanResults(full, open_ports)
        return
    
    print(f"Scanning [[red not bold]{base}(...)[/red not bold]] [[red]{'with' if portscan else 'without'}[/red]] ports and [[red not bold]{timeout}[/red not bold]]s timeout\n")
    
    ipScanner.scan()
    ipScanner.printSummary()

    while True:
        choice = input("\nEnter the number of an IP for a full port scan, or 'q' to quit\ncommand: ")
        if choice.lower() == 'q':
            break
        try:
            choice = int(choice)
            if 1 <= choice <= len(ipScanner.responsiveIps):
                ip = list(ipScanner.esponsiveIps.keys())[choice - 1]
                print(f"\nPerforming full port scan on [[red not bold]{ip}[/red not bold]]...")
                open_ports = ipScanner.fullPortScan(ip)
                ipScanner.printFullScanResults(ip, open_ports)
            else:
                print("Invalid number. Please try again.")
        except ValueError:
            print("[red]Invalid input. Please enter a number or 'q'.[/red]")

if __name__ == "__main__":
    typer.run(main)
