#For this first version, we'll use the library "subprocess" that allows us to interact with external processes as console command lines.
import subprocess

# Update: the commands are now grouped by section. This is a "nested dictionary": a dictionary inside a dictionary.
# Structure:  SECTIONS[section_key]["commands"][command_name] = (command_list, tail_lines)
# - section_key: short word used internally (cpu, memory, network...)
# - "label": the text shown in the menu
# - tail_lines: NEW, a number of lines to keep from the end of the output (None = show everything).
#   It replaces the "| tail" pipes, which don't work inside a list.
# Remember that a dictionary works with a "key" and a "value".
SECTIONS = {
    #CPU and general OS info
    "cpu": {
        "label": "CPU & OS",
        "commands": {
            "Uptime": (["uptime", "-p"], None), # OS uptime
            "Hostname Details": (["hostnamectl"], None), # Hostname details
            "CPU": (["lscpu"], None), # useful, it shows all the CPU info
        },
    },
    #Memory
    "memory": {
        "label": "Memory",
        "commands": {
            "Memory": (["free", "-h"], None), # total memory used
            "Swap show": (["swapon", "--show"], None), #active swap
        },
    },
    #Disk
    "disk": {
        "label": "Disk",
        "commands": {
            "Disk Usage": (["df", "-h"], None), # General disk usage
            "Usage + partitions": (["df", "-hT"], None), # Disk usage + partitions type
        },
    },
    #Taks manager and services
    "services": {
        "label": "Task manager & services",
        "commands": {
            "Services running": (
                ["systemctl", "list-units", "--type=service", "--state=running", "--no-pager"], None), # Services running
            "Services that starts at boot": (
                # list-units can't filter "enabled" (that is a unit file property), so we use list-unit-files
                ["systemctl", "list-unit-files", "--type=service", "--state=enabled", "--no-pager"], None), # Services defined to start at boot
        },
    },
    #Network
    "network": {
        "label": "Network",
        "commands": {
            "IP info": (["ip", "-br", "addr"], None),
            "Gateway": (["ip", "route"], None),
            "DNS": (["cat", "/etc/resolv.conf"], None),
            "Services serving traffic": (["ss", "-tulpn"], None), # Services serving traffic (Network)
        },
    },
    #Warnings
    "warnings": {
        "label": "Warnings",
        "commands": {
            "Last 5 Logins": (["last", "-n", "5"], None),
            "Last 10 general errors": (["journalctl", "-p", "err", "-b", "--no-pager", "-n", "10"], None),
            # Typo fixed ("dmesg") and a missing comma added. Here we use tail=10 to keep only the last 10 lines
            "Kernel errors": (["dmesg", "--level=err,warn"], 10),
        },
    },
}


def run_command(command, tail=None):
    # NEW: this function runs ONE command. Before, this code lived inside the big for loop,
    # now it's separated so we can reuse it for any section.
    try: # With this small try, our python program will verify failures and if necessary go with an exception
        result = subprocess.run(
            command,
            capture_output=True, # inspect command output
            text=True, # enables text mode
            check=True, # verify if the command finish with a nonzero exit status
            timeout=10 # This defines a 10sec time limit to the command execution
        )
        output = result.stdout.strip() # Removes an initial and final space of a string(including new line characters)

        if tail: # NEW: if tail has a number (not None), we keep only the last N lines
            # splitlines() converts the text into a list of lines, [-tail:] takes the last N, join() puts them back together
            output = "\n".join(output.splitlines()[-tail:])
        return output
    # Now, here we'll find our error exceptions
    except (FileNotFoundError, # If python cannot find the asked executable to run
            subprocess.CalledProcessError, # If the command finishes with a nonzero exit status and we have check=true
            subprocess.TimeoutExpired) as error: # If the execution exceeds the time defined
        return f"Unable to retrieve information: {error}" #this is a very important line in the program:
        #Insted of finish all the script, this allows to finish the script and in case of a failure it will print an error


def run_section(key):
    # NEW: runs every command of one section and prints the result.
    section = SECTIONS[key]
    print(f"\n=========||° {section['label'].upper()} °||=========")

    # In this case we're using a "for loop" due to we had a finite collection of commands to process
    # Dictionaries had a method called .items(), it provides an iterable view to the dictionaries key-value pairs. (name-command)
    # Here each value is a tuple (command, tail), so we "unpack" it directly in the loop: name, (command, tail)
    for name, (command, tail) in section["commands"].items():
        print(f"\n________==|| {name} ||==________")
        print(run_command(command, tail))


def show_menu():
    # NEW: builds the menu from the SECTIONS dictionary, so if you add a new section it appears here automatically.
    print("\n--- Linux System Audit ---")
    keys = list(SECTIONS) # list(dictionary) gives us only the keys: ["cpu", "memory", "disk", ...]
    for number, key in enumerate(keys, start=1): # enumerate gives us a counter (starting at 1) + each key
        print(f"  {number}. {SECTIONS[key]['label']}")
    print("  a. All sections")
    print("  q. Quit")
    return keys # we return the list so main() can translate the number typed by the user into a section key


def main():
    while True: # NEW: the menu repeats until the user chooses to quit
        keys = show_menu()
        # input() waits for the user to type. strip() removes spaces and lower() makes "A" and "a" equal
        choice = input("\nChoose (e.g. 2 or 1,3,5): ").strip().lower()

        if choice == "q":
            break # exits the while loop, so the program ends
        if choice == "a":
            selected = keys # all the sections
        else:
            selected = [] # empty list where we'll save the valid sections chosen
            for part in choice.split(","): # "1,3,5" -> ["1", "3", "5"]
                part = part.strip()
                # isdigit() checks it's a number, then we verify it's inside the menu range
                if part.isdigit() and 1 <= int(part) <= len(keys):
                    selected.append(keys[int(part) - 1]) # -1 because lists start at 0 but the menu starts at 1
                else:
                    print(f"Invalid option: '{part}'")

        for key in selected:
            run_section(key)


if __name__ == "__main__": # this runs main() only when the file is executed directly, not when it's imported
    main()