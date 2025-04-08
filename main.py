import os
import msvcrt
import psutil
import subprocess
import shutil
from pathlib import Path
import time
from colorama import init, Fore, Style

init(autoreset=True)

def clear():
    os.system("cls" if os.name == "nt" else "clear")

def get_removable_drives():
    drives = []
    for part in psutil.disk_partitions(all=False):
        if 'removable' in part.opts.lower():
            drives.append(part.device)
    return drives

def read_key():
    key = msvcrt.getch()
    if key == b'\xe0':
        key = msvcrt.getch()
        if key == b'H':
            return "up"
        elif key == b'P':
            return "down"
    elif key == b'\r':
        return "enter"
    return None

def display_menu(items, title="Select an option"):
    index = 0
    while True:
        clear()
        print(Fore.MAGENTA + Style.BRIGHT + f"\n{title}\n")
        for i, item in enumerate(items):
            if i == index:
                print(Fore.GREEN + f"> {item}")
            else:
                print(f"  {item}")
        key = read_key()
        if key == "up":
            index = (index - 1) % len(items)
        elif key == "down":
            index = (index + 1) % len(items)
        elif key == "enter":
            time.sleep(0.2)
            return items[index]

def select_usb_drive():
    drives = get_removable_drives()
    if not drives:
        print(Fore.RED + "No USB drives found.")
        exit(1)
    return display_menu(drives, "Select a USB drive")

def select_python_script():
    assets = Path("assets")
    if not assets.exists():
        print(Fore.RED + "'assets' folder not found.")
        exit(1)
    scripts = sorted([f for f in assets.glob("*.py") if f.is_file()])
    if not scripts:
        print(Fore.RED + "No .py scripts in 'assets' folder.")
        exit(1)
    names = [str(f.name) for f in scripts]
    chosen = display_menu(names, "Select script to build")
    for f in scripts:
        if f.name == chosen:
            return f
    return None

def build_executable(script_path):
    print(Fore.YELLOW + "\n⚙️  Building executable...")
    script_dir = script_path.parent
    script_file = script_path.name
    cmd = [
        "pyinstaller",
        "--onefile",
        "--noconsole",
        script_file
    ]

    proc = subprocess.Popen(cmd, cwd=script_dir, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    spinner = ['⠋', '⠙', '⠹', '⠸', '⠼', '⠴', '⠦', '⠧', '⠇', '⠏']
    bar_width = 30
    progress = 0
    index = 0

    while proc.poll() is None:
        filled = int((progress / 100) * bar_width)
        bar = f"{Fore.GREEN}{'█' * filled}{Fore.WHITE}{'-' * (bar_width - filled)}"
        print(f"\r{spinner[index % len(spinner)]} [{bar}] {progress}%", end='', flush=True)
        time.sleep(0.1)
        progress = min(progress + 1, 100)
        index += 1

    progress = 100
    filled = bar_width
    bar = f"{Fore.GREEN}{'█' * filled}"
    print(f"\r✔️  [{bar}] 100%")
    
    exe_path = script_dir / "dist" / script_path.stem
    exe_path = exe_path.with_suffix(".exe")
    if exe_path.exists():
        print(Fore.GREEN + "\n✔️  Build successful!\n")
        return exe_path
    else:
        print(Fore.RED + "\n❌ Executable build failed.\n")
        return None


def create_autorun(drive, exe_name):
    path = os.path.join(drive, "autorun.inf")
    with open(path, "w") as f:
        f.write("[autorun]\n")
        f.write(f"open={exe_name}\n")
        f.write("label=Brainrot Builder\n")
    print(Fore.BLUE + f"autorun.inf created at {path}")

def deploy_to_usb(drive, exe_path):
    if not os.path.exists(drive):
        print(Fore.RED + "USB drive not found.")
        return
    target = os.path.join(drive, os.path.basename(exe_path))
    shutil.copy(exe_path, target)
    create_autorun(drive, os.path.basename(exe_path))
    print(Fore.GREEN + f"Deployed to {drive}")

def cleanup_build_artifacts(script_path):
    base = script_path.parent
    paths = [
        base / (script_path.stem + ".spec"),
        base / "build",
        base / "dist"
    ]
    for p in paths:
        try:
            if p.exists():
                if p.is_file():
                    p.unlink()
                else:
                    shutil.rmtree(p)
                print(Fore.BLUE + f"Removed {p}")
        except Exception as e:
            print(Fore.RED + f"Could not remove {p}: {e}")
    print(Fore.BLUE + "Cleanup done.")

def format_drive(drive):
    drive = drive.rstrip("\\")
    print(Fore.RED + f"WARNING: {drive} will be formatted!")
    confirm = input("Type YES to continue: ")
    if confirm != "YES":
        print(Fore.RED + "Format aborted.")
        exit(1)
    cmd = f'echo Y | format {drive} /q /fs:NTFS /v:USB /x'
    subprocess.call(cmd, shell=True)
    print(Fore.BLUE + f"{drive} formatted.")

def main():
    clear()
    usb = select_usb_drive()
    format_drive(usb)
    script = select_python_script()
    exe = build_executable(script)
    if exe:
        deploy_to_usb(usb, exe)
        cleanup_build_artifacts(script)
    else:
        print(Fore.RED + "Executable not created.")

if __name__ == "__main__":
    main()
