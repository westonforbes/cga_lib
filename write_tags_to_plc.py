from cga_lib.interface_rslinx import InterfaceRsLinx
from cga_lib.data_processors import DataProcessors
import pyperclip
from wf_console import Console
from wf_console.constants import Constants as color


supported_data_types = [
                        "BOOL",
                        "SINT",
                        "INT",
                        "DINT",
                        "LINT",
                        "USINT",
                        "UINT",
                        "UDINT",
                        "REAL",
                        "LREAL",
                        "STRING"
]

def write_tag_result(message: str, good: bool = True):
    """
    #### Description:
    Callback handler for status messages from InterfaceRsLinx methods.
    
    #### Args:
        message (str): The status message to display.
    """
    if good:
        Console.fancy_print(f"<GOOD>{message}</GOOD>")
    else:
        Console.fancy_print(f"<BAD>{message}</BAD>")

def _validate_and_format_tag_write_data(content: str) -> dict:

    try:
        tag_dict = {}
        lines = content.strip().split('\n')
        for line in lines:
            line = line.strip('\r')
            parts = line.split('\t')
            
            # Split the line into tag_address, value, and data_type.
            tag_address = parts[0]
            value = parts[1]
            data_type = parts[2].upper()

            # Check that the data type for the current tag is supported.
            if data_type not in supported_data_types: 
                Console.fancy_print(f"<BAD>unsupported data type '{data_type}' for tag '{tag_address}'</BAD>\n")
                pass
            else:
                # Convert the value to the appropriate type based on data_type.
                if data_type == "BOOL":
                    tag_dict[tag_address] = True if value.lower() in ['1', 'true', 'yes'] else False
                elif data_type in ["SINT", "INT", "DINT", "LINT"]:
                    tag_dict[tag_address] = int(value)
                elif data_type in ["USINT", "UINT", "UDINT"]:
                    tag_dict[tag_address] = int(value)
                elif data_type in ["REAL", "LREAL"]:
                    tag_dict[tag_address] = float(value)
                elif data_type == "STRING":
                    tag_dict[tag_address] = str(value)

        return tag_dict
    except Exception as e:
        raise Exception(f"error converting string to tag dictionary: {e}")


def _correct_column_count(clipboard_data: str, column_count: int) -> bool:
    lines = clipboard_data.strip().split('\n')
    for line in lines:
        columns = line.split('\t')
        if len(columns) != column_count:
            return False
    return True


def routine():
    
    # Clear the console.
    Console.clear() 
    
    # Print the header and instructions.
    Console.fancy_print(f"\n<MENU_TITLE>---write tags to plc---</MENU_TITLE>")
    Console.fancy_print("\nto use this module, copy excel data to clipboard in the following format:")
    Console.fancy_print("column 1: tag_address")
    Console.fancy_print("column 2: value")
    Console.fancy_print("column 3: data_type")
    Console.fancy_print("<BAD>do not include headers or extra columns.</BAD>")

    # Prompt the user to copy data to clipboard.
    choice = Console.fancy_input("<INPUT_PROMPT>\npress enter to copy clipboard and continue or type 'back': </INPUT_PROMPT>")

    # If the user typed "back", return.
    if choice.lower() == "back": return

    # If the user pressed enter...
    if choice == '':

        # Clear the console.
        Console.clear()

        # Print the header.
        Console.fancy_print(f"\n<MENU_TITLE>---write tags to plc---</MENU_TITLE>")

        # Get the data from the clipboard.
        clipboard_data = pyperclip.paste()

        # Check the clipboard data is three columns of data...
        if not _correct_column_count(clipboard_data, 3):
            Console.fancy_print("\n<BAD>clipboard data malformed. Check that your selection is only three columns (tag_address, value, data_type) and rerun.</BAD>")
            Console.press_enter_pause()
            return
        
        else:
            converted_data = _validate_and_format_tag_write_data(clipboard_data)
            
            # Prompt the user for the PLC IP address.
            plc_ip = Console.fancy_input("<INPUT_PROMPT>\nenter plc ip address or type 'back': </INPUT_PROMPT>")
        
            # If the user did not type "back"...
            if plc_ip.lower() != "back":
                Console.fancy_print(f"press 'ctrl+c' to cancel operation.")
                Console.fancy_print(f"writing tags to plc at ip '{plc_ip}'...")
                try:
                    InterfaceRsLinx.write_tags(plc_ip, converted_data, callback=write_tag_result)
                except KeyboardInterrupt:
                    Console.clear()
                    Console.fancy_print(f"\n<MENU_TITLE>---write tags to plc---</MENU_TITLE>")
                    Console.fancy_print(f"\n<WARNING>operation cancelled by user.</WARNING>")
                    Console.press_enter_pause()
                except Exception as e:
                    Console.clear()
                    Console.fancy_print(f"\n<MENU_TITLE>---write tags to plc---</MENU_TITLE>")
                    Console.fancy_print(f"<BAD>error: {e}</BAD>")
                    Console.press_enter_pause()
                Console.fancy_print(f"<GREEN>operation complete. press enter to return to main menu.</GREEN>")
                Console.press_enter_pause()
