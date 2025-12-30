from cga_lib.interface_rslinx import InterfaceRsLinx
from cga_lib.data_processors import DataProcessors
import pyperclip
import write_tags_to_plc
from wf_console import Console
from wf_console.constants import Constants as color
from tkinter import Tk, filedialog

def status_callback(message: str):
    """
    #### Description:
    Callback handler for status messages from InterfaceRsLinx methods.
    
    #### Args:
        message (str): The status message to display.
    """
    Console.clear_last_line()
    Console.fancy_print(f"<GOOD>{message}</GOOD>")

def save_file_dialog(default_extension: str = ".csv", file_types: list = [("CSV files", "*.csv"), ("All files", "*.*")]) -> str:
    """
    #### Description:
    Opens a file save dialog and returns the selected file path.
    
    #### Args:
        default_extension (str): The default file extension for the save dialog.
        file_types (list): A list of tuples specifying the file types for the dialog.
    
    #### Returns:
        str: The selected file path or an empty string if cancelled.
    """
    root = Tk()
    root.withdraw()
    root.attributes('-topmost', True)
    file_path = filedialog.asksaveasfilename(defaultextension=default_extension, filetypes=file_types)
    root.destroy()
    root.update()
    return file_path

def get_all_plc_tags():
    
    # Clear the console and print the header.
    Console.clear(); Console.fancy_print(f"\n<MENU_TITLE>---get all plc tags---</MENU_TITLE>")
    
    # Prompt the user for the PLC IP address.
    plc_ip = Console.fancy_input("<INPUT_PROMPT>\nenter plc ip address or type 'back': </INPUT_PROMPT>")
    
    # If the user did not type "back"...
    if plc_ip.lower() != "back":
        Console.fancy_print(f"press 'ctrl+c' to cancel operation.")
        Console.fancy_print(f"getting all tags from plc at ip '{plc_ip}'...")
        try:
            data = InterfaceRsLinx.get_all_available_tags(plc_ip, callback=status_callback)
            data_str = DataProcessors.tag_dict_to_tab_delimited_string(data)
            pyperclip.copy(data_str)
            Console.clear()
            Console.fancy_print(f"\n<MENU_TITLE>---get all plc tags---</MENU_TITLE>")
            Console.fancy_print(f"\n<GOOD>done. all tags copied to clipboard. paste into microsoft excel or other spreadsheet program.</GOOD>")
            selection = Console.fancy_input("<INPUT_PROMPT>would you like to save the output to a csv file? (y/n): </INPUT_PROMPT>")
    
            if selection.lower() == 'y' or selection.lower() == 'yes':
                Console.clear_last_line()
                Console.clear_last_line()
                Console.fancy_print("<BAD>Understood. We recommend using the data on your clipboard over csv where possible,</BAD>")
                Console.fancy_print("<BAD>as csv files are susceptible to misalignment when tags contain commas or newlines.</BAD>")
                Console.fancy_print("<BAD>Press enter to launch save dialog window. Press cancel in dialog window to return to main menu.</BAD>")
                Console.press_enter_pause()
                file_path = save_file_dialog()

                if file_path:
                    Console.clear_last_line()
                    Console.clear_last_line()
                    Console.clear_last_line()
                    Console.clear_last_line()
                    try:
                        DataProcessors.save_tags_to_csv(data_str, file_path)
                        Console.fancy_print(f"<GOOD>tags saved to {file_path}</GOOD>")
                        Console.press_enter_pause()
                    except Exception as e:
                        Console.fancy_print(f"<BAD>{e}</BAD>")
                        Console.press_enter_pause()

        except KeyboardInterrupt:
            Console.clear()
            Console.fancy_print(f"\n<MENU_TITLE>---get all plc tags---</MENU_TITLE>")
            Console.fancy_print(f"\n<WARNING>operation cancelled by user.</WARNING>")
            Console.press_enter_pause()
        except Exception as e:
            Console.clear()
            Console.fancy_print(f"\n<MENU_TITLE>---get all plc tags---</MENU_TITLE>")
            Console.fancy_print(f"<BAD>error: {e}</BAD>")
            Console.press_enter_pause()

def get_plc_time():
    """
    #### Description:
    Retrieves and displays the current time from the specified PLC.
    """
    
    # Clear the console and print the header.
    Console.clear(); Console.fancy_print(f"\n<MENU_TITLE>---get plc time---</MENU_TITLE>")
    
    # Prompt the user for the PLC IP address.
    plc_ip = Console.fancy_input("<INPUT_PROMPT>\nenter plc ip address or type 'back': </INPUT_PROMPT>")
    
    # If the user did not type "back"...
    if plc_ip.lower() != "back":

        # Execute the time retrieval operation.
        Console.clear_last_line()
        Console.fancy_print(f"getting time from plc at ip '{plc_ip}'...")
        try:
            result = InterfaceRsLinx.get_plc_time(plc_ip)
            Console.fancy_print(f"<GOOD>plc time: {result.Value.year}-{result.Value.month}-{result.Value.day} {result.Value.hour}:{result.Value.minute}:{result.Value.second}</GOOD>")
        except Exception as e:
            Console.fancy_print(f"<BAD>{e}</BAD>")
        
        # Pause before returning to menu.
        Console.press_enter_pause()

def set_plc_time():
    """
    #### Description:
    Sets the PLC time to match the computer's current time.
    """
    
    # Clear the console and print the header.
    Console.clear(); Console.fancy_print(f"\n<MENU_TITLE>---set plc time---</MENU_TITLE>")
    
    # Prompt the user for the PLC IP address.
    plc_ip = Console.fancy_input("<INPUT_PROMPT>\nenter plc ip address or type 'back': </INPUT_PROMPT>")
    
    # If the user did not type "back"...
    if plc_ip.lower() != "back":

        # Execute the time setting operation.
        Console.clear_last_line()
        Console.fancy_print(f"setting time on plc at ip '{plc_ip}'...")
        try:
            InterfaceRsLinx.set_plc_time(plc_ip)
            Console.fancy_print(f"<GOOD>plc time set successfully.</GOOD>")
        except Exception as e:
            Console.fancy_print(f"<BAD>{e}</BAD>")

        # Pause before returning to menu.
        Console.press_enter_pause()

if __name__ == "__main__":

    # Override colors used in the Console class.
    Console.TAG_MAP["MENU_TITLE"] = color.RESET
    Console.TAG_MAP["MENU_ITEM"] = color.RESET
    Console.TAG_MAP["MENU_KEY"] = color.RESET
    Console.TAG_MAP["MENU_SELECTION_PROMPT"] = color.RESET
    Console.TAG_MAP["INPUT_PROMPT"] = color.RESET

    while True:

        # Clear the console.
        Console.clear()

        # Define the menu options.
        option_1 = "get all plc tags, with UDT crawling - <BAD>still some work needed, complex udts can cause issues</BAD>"
        option_2 = "get all plc tags, without UDT crawling - <WARNING>refactoring</WARNING>"
        option_3 = "write tags to plc - <WARNING>refactoring</WARNING>"
        option_4 = "get plc time - <GOOD>COMPLETE: documented, unit tested, reviewed frontend & backend methods</GOOD>"
        option_5 = "set plc time to computer time - <GOOD>COMPLETE: documented, unit tested, reviewed frontend & backend methods</GOOD>"
        menu_options = [option_1, option_2, option_3, option_4, option_5, "exit"]

        # Print the menu and get user selection.
        int_selection, string_selection = Console.integer_only_menu_with_validation(title="CG Automation Library - RsLinx Interface", item_list=menu_options)
        
        # Route based on selection.
        if string_selection == option_1: get_all_plc_tags()
        if string_selection == option_2: get_all_plc_tags()
        if string_selection == option_3: write_tags_to_plc.routine()
        if string_selection == option_4: get_plc_time()
        if string_selection == option_5: set_plc_time()
        if string_selection == "exit": break