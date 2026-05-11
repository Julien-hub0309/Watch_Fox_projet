from scapy.all import sniff, IP, TCP, UDP, ICMP
from utile.display import console

class NetworkSniffer:
    def __init__(self, target=None):
        self.target = target # On pourrait filtrer par IP cible si besoin

    def analyser_paquet(self, paquet):
        if paquet.haslayer(IP):
            ip_src = paquet[IP].src
            ip_dst = paquet[IP].dst
            proto = "Autre"
            if paquet.haslayer(TCP): proto = "TCP"
            elif paquet.haslayer(UDP): proto = "UDP"
            elif paquet.haslayer(ICMP): proto = "ICMP"
            
            console.print(f"[bold green][+][/bold green] {proto} : {ip_src} --> {ip_dst}")

    def run_scan(self):
        console.print(f"[bold orange1]📡 Démarrage du sniffing sur {self.target if self.target else 'tout le réseau'}...[/bold orange1]")
        console.print("[italic]Appuyez sur Ctrl+C pour arrêter[/italic]\n")
        try:
            # Si target est une IP, on ajoute un filtre
            filtre = f"host {self.target}" if self.target else "ip"
            sniff(filter=filtre, prn=self.analyser_paquet, store=False)
        except Exception as e:
            console.print(f"[bold red]Erreur : {e}[/bold red]")