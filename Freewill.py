import os
os.system('pip install windows-curses win32com.client')
os.system('timeout /t 1')
import curses
import winreg
import win32com.client

def set_env_var(name, value, is_system=False):
    try:
        if is_system:
            reg_key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r'SYSTEM\CurrentControlSet\Control\Session Manager\Environment', 0, winreg.KEY_SET_VALUE)
        else:
            reg_key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r'Environment', 0, winreg.KEY_SET_VALUE)
        winreg.SetValueEx(reg_key, name, 0, winreg.REG_SZ, value)
        winreg.CloseKey(reg_key)
        print(f"Environment variable '{name}' set to '{value}'")
    except Exception as e:
        print(f"Error setting environment variable '{name}': {e}")

def create_shortcut(target_path, shortcut_path):
    shell = win32com.client.Dispatch('WScript.Shell')
    shortcut = shell.CreateShortCut(shortcut_path)
    shortcut.TargetPath = target_path
    shortcut.save()

def remove_shortcut(shortcut_path):
    if os.path.exists(shortcut_path):
        os.remove(shortcut_path)

def get_startup_folder():
    return os.path.join(os.getenv('APPDATA'), 'Microsoft', 'Windows', 'Start Menu', 'Programs', 'Startup')

def get_temp_folder():
    return os.getenv('TEMP')

def get_status_from_shortcuts(startup_folder):
    status = {
        'CleanDownloadsOnBoot': 'Disabled',
        'CleanScreenshotsOnBoot': 'Disabled',
        'CleanTempOnBoot': 'Disabled',
        'CleanPrefixFolders': 'Disabled'
    }
    
    shortcuts = {
        'CleanDownloadsOnBoot': 'CleanDownloadsService.lnk',
        'CleanScreenshotsOnBoot': 'CleanScreenshotsService.lnk',
        'CleanTempOnBoot': 'CleanTempOnBootService.lnk',
        'CleanPrefixFolders': 'CleanPrefixFoldersService.lnk'
    }
    
    for key, filename in shortcuts.items():
        if os.path.exists(os.path.join(startup_folder, filename)):
            status[key] = 'Enabled'
    
    return status

def print_centered(stdscr, text, y_offset=0):
    h, w = stdscr.getmaxyx()
    lines = text.split('\n')
    for idx, line in enumerate(lines):
        x = w // 2 - len(line) // 2
        y = idx + y_offset
        stdscr.addstr(y, x, line)

def main(stdscr):
    curses.curs_set(0)
    stdscr.keypad(True)
    curses.start_color()
    curses.init_pair(1, curses.COLOR_BLACK, curses.COLOR_WHITE)
    curses.init_pair(2, curses.COLOR_WHITE, curses.COLOR_BLACK)

    stdscr.clear()
    menu = ['Clean Downloads', 'Clean Screenshots', 'Clean Temp', 'DesktopPrefixFolderCleaner', 'Exit Tool']
    selected = [False] * len(menu)
    current_row = 0

    startup_folder = get_startup_folder()
    temp_folder = get_temp_folder()
    modules_folder = os.path.join(os.path.dirname(__file__), 'modules')

    ascii_art = """
    ░        ░░░      ░░░░      ░░░       ░░░        ░░  ░░░░  ░░░      ░░░  ░░░░  ░░        ░░  ░░░░  ░
    ▒▒▒▒  ▒▒▒▒▒  ▒▒▒▒▒▒▒▒  ▒▒▒▒  ▒▒  ▒▒▒▒  ▒▒  ▒▒▒▒▒▒▒▒  ▒▒▒▒  ▒▒  ▒▒▒▒▒▒▒▒  ▒▒▒  ▒▒▒▒▒▒  ▒▒▒▒▒▒  ▒▒  ▒▒
    ▓▓▓▓  ▓▓▓▓▓▓      ▓▓▓  ▓▓▓▓  ▓▓       ▓▓▓      ▓▓▓▓▓  ▓▓  ▓▓▓▓      ▓▓▓     ▓▓▓▓▓▓▓▓  ▓▓▓▓▓▓▓    ▓▓▓
    ████  ███████████  ██        ██  ███  ███  ██████████    ██████████  ██  ███  ██████  ████████  ████
    ████  ██████      ███  ████  ██  ████  ██        █████  ██████      ███  ████  ██        █████  ████
                            The changes will be applied after rebooting the PC.
                            
USDT DONATION UQCjpuXkzQXbqxGRtBSafGVqP4sDeMRE-Wd7rax0Mj0slODD"""

    while True:
        stdscr.clear()
        print_centered(stdscr, ascii_art)

        h, w = stdscr.getmaxyx()
        env_status = get_status_from_shortcuts(startup_folder)
        status_y = len(ascii_art.split('\n')) + 1
        env_status_lines = [
            f"Clean Downloads On Boot: {env_status['CleanDownloadsOnBoot']}",
            f"Clean Screenshots On Boot: {env_status['CleanScreenshotsOnBoot']}",
            f"Clean Temp On Boot: {env_status['CleanTempOnBoot']}",
            f"Clean Prefix Folders: {env_status['CleanPrefixFolders']}"
        ]
        for idx, line in enumerate(env_status_lines):
            stdscr.addstr(status_y + idx, w // 2 - len(line) // 2, line)

        stdscr.addstr(status_y + len(env_status_lines) + 1, w // 2 - len(f"Startup Folder: {startup_folder}") // 2, f"Startup Folder: {startup_folder}")
        stdscr.addstr(status_y + len(env_status_lines) + 2, w // 2 - len(f"Temp Folder: {temp_folder}") // 2, f"Temp Folder: {temp_folder}")

        menu_y = status_y + len(env_status_lines) + 4
        for idx, row in enumerate(menu):
            x = w // 2 - len(row) // 2
            y = menu_y + idx
            if idx == current_row:
                if selected[idx]:
                    row = row + " V"
                stdscr.attron(curses.color_pair(1))
                stdscr.addstr(y, x, row)
                stdscr.attroff(curses.color_pair(1))
            else:
                if selected[idx]:
                    row = row + " V"
                stdscr.attron(curses.color_pair(2))
                stdscr.addstr(y, x, row)
                stdscr.attroff(curses.color_pair(2))
        
        stdscr.refresh()

        key = stdscr.getch()

        if key == curses.KEY_DOWN:
            current_row = (current_row + 1) % len(menu)
        elif key == curses.KEY_UP:
            current_row = (current_row - 1) % len(menu)
        elif key == curses.KEY_ENTER or key in [10, 13]:
            if menu[current_row] == 'Exit Tool':
                break
            else:
                selected[current_row] = not selected[current_row]

                exe_files = {
                    'Clean Downloads': 'CleanDownloadsService.exe',
                    'Clean Screenshots': 'CleanScreenshotsService.exe',
                    'Clean Temp': 'CleanTempOnBootService.exe',
                    'DesktopPrefixFolderCleaner': 'CleanPrefixFoldersService.exe'
                }

                shortcut_filenames = {
                    'Clean Downloads': 'CleanDownloadsService.lnk',
                    'Clean Screenshots': 'CleanScreenshotsService.lnk',
                    'Clean Temp': 'CleanTempOnBootService.lnk',
                    'DesktopPrefixFolderCleaner': 'CleanPrefixFoldersService.lnk'
                }

                exe_file = exe_files[menu[current_row]]
                shortcut_filename = shortcut_filenames[menu[current_row]]
                shortcut_path = os.path.join(startup_folder, shortcut_filename)
                exe_path = os.path.join(modules_folder, exe_file)

                if selected[current_row]:
                    set_env_var(menu[current_row].replace(' ', '') + 'OnBoot', '1')
                    create_shortcut(exe_path, shortcut_path)
                else:
                    set_env_var(menu[current_row].replace(' ', '') + 'OnBoot', '0')
                    remove_shortcut(shortcut_path)

                stdscr.clear()
                print_centered(stdscr, ascii_art)
                stdscr.addstr(h // 2, w // 2 - len(menu[current_row]) // 2, f'You Choosed: {menu[current_row]} Press Enter To Return')
                stdscr.refresh()
                stdscr.getch()
        else:
            continue

curses.wrapper(lambda stdscr: main(stdscr))
