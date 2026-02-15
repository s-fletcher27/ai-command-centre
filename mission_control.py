import time
import subprocess
import json
import shutil
import psutil
from datetime import datetime
from rich.console import Console
from rich.layout import Layout
from rich.panel import Panel
from rich.table import Table
from rich.live import Live
from rich.align import Align
from rich.text import Text
from rich import box 

console = Console()

# --- THE ART: Cylindrical Crest with Single Stable Spinner ---
def get_crest_visual(current_sec):
    """Restored stable single-line spinner for perfect alignment"""
    # 12 positions for the 60-second cycle (updates every 5s)
    chars = ["|", "/", "-", "\\", "|", "/", "-", "\\", "|", "/", "-", "\\"]
    index = (current_sec // 5) % 12
    spinner = chars[index]

    visual = Text()
    # Header
    visual.append("\n      ★      \n", style="bold yellow")
    visual.append("   COMMAND   \n", style="bold white")
    
    # Cylindrical Shield - Exact character counts to prevent "shifting"
    visual.append("\n   .-----.   \n", style="bold white")
    visual.append(r"  /       \  ", style="bold white")
    visual.append("\n")
    visual.append(r" |         | ", style="bold white")
    visual.append("\n")
    # The Single Spinner Core (Rock solid alignment)
    visual.append(f" |    {spinner}    | ", style="bold green") 
    visual.append("\n")
    visual.append(r" |         | ", style="bold white")
    visual.append("\n")
    visual.append(r"  \       /  ", style="bold white")
    visual.append("\n   '-----'   \n", style="bold white")
    
    visual.append("\n  NODE: PI5  \n", style="bold cyan")
    visual.append("  VER: 1.8   ", style="dim white")
    return visual

# --- DATA FETCHING ---
def get_system_stats():
    try:
        cpu_pct = psutil.cpu_percent()
        ram = psutil.virtual_memory()
        try:
            temp = subprocess.check_output("vcgencmd measure_temp", shell=True, timeout=1, text=True)
            temp = temp.replace("temp=", "").replace("'", "°").strip()
        except:
            temp = "N/A"
        return cpu_pct, ram.percent, temp
    except:
        return 0, 0, "N/A"

def get_uptime():
    try:
        boot_time = datetime.fromtimestamp(psutil.boot_time())
        uptime = datetime.now() - boot_time
        return str(uptime).split('.')[0]
    except:
        return "Unknown"

def get_gcp_status():
    try:
        if not shutil.which("gcloud"):
            return "[bold red]● MISSING SDK[/bold red]", "N/A"
        result = subprocess.run(
            ["gcloud", "compute", "instances", "list", "--format=json", "--filter=name=ai-lab-spot"],
            capture_output=True, text=True, timeout=2
        )
        data = json.loads(result.stdout)
        if not data:
            return "[bold dim]● STOPPED[/bold dim]", "OFFLINE"
        status = data[0]['status']
        ip = data[0]['networkInterfaces'][0]['accessConfigs'][0].get('natIP', 'No IP')
        if status == "RUNNING":
            return f"[bold green blink]● ONLINE[/bold green blink]", f"[cyan]{ip}[/cyan]"
        return f"[dim]● {status}[/dim]", "OFFLINE"
    except:
        return "[red]CHECKING..[/red]", "-"

def get_jenkins_status():
    try:
        result = subprocess.run(
            ["docker", "inspect", "-f", "{{.State.Status}}", "jenkins"],
            capture_output=True, text=True, timeout=1
        )
        if result.stdout.strip() == "running":
            return "[bold green]ACTIVE[/bold green]"
        return "[bold red]OFFLINE[/bold red]"
    except:
        return "[dim]WAITING..[/dim]"

def get_tailscale_ip():
    try:
        cmd = shutil.which("tailscale") or "/usr/sbin/tailscale"
        result = subprocess.run([cmd, "ip", "-4"], capture_output=True, text=True, timeout=1)
        return result.stdout.strip() or "No Network"
    except:
        return "-"

# --- LAYOUT ---
def make_layout():
    layout = Layout()
    layout.split(
        Layout(name="header", size=3),
        Layout(name="body", ratio=1),
        Layout(name="footer", size=1)
    )
    layout["body"].split_row(
        Layout(name="left", ratio=1),
        Layout(name="right", ratio=2), 
    )
    layout["right"].split_column(
        Layout(name="cloud_panel", ratio=1),
        Layout(name="local_panel", ratio=1),
    )
    return layout

def generate_table(data_dict, style_color):
    table = Table(expand=True, box=None, padding=(0, 2))
    table.add_column("Metric", style=style_color, justify="left")
    table.add_column("Value", justify="right")
    for key, value in data_dict.items():
        table.add_row(key, Text.from_markup(str(value)))
    return table

# --- EXECUTION ---
layout = make_layout()

with Live(layout, refresh_per_second=1, screen=True) as live:
    while True:
        now_dt = datetime.now()
        current_sec = now_dt.second
        
        # Fetch Data
        cpu_val, ram_val, temp = get_system_stats()
        gcp_state, gcp_ip = get_gcp_status()
        jenkins_state = get_jenkins_status()
        ts_ip = get_tailscale_ip()
        uptime = get_uptime()

        # Update Header
        layout["header"].update(
            Panel(Align.center(f"[bold white]🚀 AI COMMAND CENTER[/bold white] | [bold yellow]{now_dt.strftime('%H:%M:%S')}[/bold yellow]"), 
            style="on blue", box=box.SQUARE)
        )
        
        # Update Left (Stable Crest)
        layout["left"].update(
            Panel(Align.center(get_crest_visual(current_sec), vertical="middle"), 
                  title="COMMANDER", border_style="bold green", box=box.HEAVY)
        )

        # Update Cloud Panel
        layout["cloud_panel"].update(
            Panel(Align.center(generate_table({"Region": "us-central1", "Status": gcp_state, "Public IP": gcp_ip}, "cyan"), vertical="middle"), 
                    title="GOOGLE CLOUD", border_style="bold cyan", box=box.HEAVY)
        )

        # Update Local Panel
        layout["local_panel"].update(
            Panel(Align.center(generate_table({"Uptime": uptime, "Jenkins": jenkins_state, "Network": ts_ip, "CPU/RAM": f"{cpu_val}% / {ram_val}%", "Temp": temp}, ">
                    title="LOCAL BASE", border_style="bold magenta", box=box.HEAVY)
        )

        # Update Footer
        layout["footer"].update(Text(" MISSION CONTROL ACTIVE | CTRL+C TO TERMINAL ", style="black on white", justify="center"))

        # --- 5-SECOND SYNC ---
        now_ts = time.time()
        time_to_sleep = 5.0 - (now_ts % 5.0)
        if time_to_sleep < 0.1: time_to_sleep = 5
        time.sleep(time_to_sleep)

