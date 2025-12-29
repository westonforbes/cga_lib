import re
from pylogix import PLC
from datetime import datetime, timezone
import concurrent.futures
from ping3 import ping
from wf_console import Console
from wf_console.constants import Constants as color
import pyperclip
from data_processors import DataProcessors
import sys

class InterfaceRsLinx:

    @staticmethod
    def _precheck_device(ip: str) -> bool:
        """
        #### Description:
        Precheck the device at the given IP address.
        #### Args:
            ip (str): IP address.
        #### Returns:
            bool: True if all checks pass, raises exception otherwise.
        """

        # Validate the IP address format.
        InterfaceRsLinx._validate_ip(ip)

        # Ping the IP address to check reachability.
        InterfaceRsLinx._ping_ip(ip)

        # Validate that the IP address belongs to a PLC.
        InterfaceRsLinx._validate_ip_is_plc(ip)

        # Indicate success.
        return True

    @staticmethod
    def _validate_ip(ip: str) -> bool:
        """
        #### Description:
        Validate the format of a  address.
        #### Args:
            ip (str): IP address.
        #### Returns:
            bool: True if valid, raises exception if invalid.
        """

        # Validate the datatype of the IP address.
        if not isinstance(ip, str): raise TypeError("ip address failed type check. expected str.")

        # Verify the IP address is valid. This is regex dark magic, stolen from the internet.
        ip_pattern = re.compile(r'^((25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$')
        if not ip or not ip_pattern.match(str(ip)): raise ValueError("ip address failed ipv4 check.")

        # Indicate success.
        return True

    @staticmethod
    def _ping_ip(ip: str, timeout: int = 1) -> bool:
        """
        Ping an IP address to check if it's reachable.
        """
        try:
            response = ping(ip, timeout=timeout, unit='s')
            if response is None or response is False:
                raise Exception(f"no response from ip '{ip}'.")
            return True
        except Exception as e:
            raise Exception(f"{e}")

    @staticmethod
    def _validate_ip_is_plc(ip: str) -> bool:
        """
        #### Description:
        Validate that the IP address belongs to a PLC.
        #### Args:
            ip (str): IP address.
        #### Returns:
            bool: True if IP belongs to a PLC, raises exception otherwise.
        """
    
        # Create a plc connection object with the context manager.
        with PLC() as device:

            # Set the ip address of the device.
            device.IPAddress = ip

            # Get device properties.
            properties = device.GetDeviceProperties()

            # If the device type is PLC, return True.
            if properties.Value.DeviceType == 'Programmable Logic Controller': return True
            
            # If not, raise an exception.
            else: raise Exception(f"device at ip '{ip}' is not a plc.")

    @staticmethod
    def read_tags(plc_ip: str, tag_list: list[str], callback=None) -> dict:
        """
        #### Description:
        Read tags from the PLC.
        
        #### Args:
            plc_ip (str): IP address of the PLC.
            tag_list (list): List of tag names to read.
            callback: Optional callback function to receive status messages.
        
        #### Returns:
            Dictionary with tag names as keys and values.
        """

        # Precheck the device.
        InterfaceRsLinx._precheck_device(plc_ip)

        # Create a dictionary to hold results YELLOW.
        results = {}
        
        # Create a plc connection object with the context manager.
        with PLC() as plc:
            
            # Set the ip address of the PLC.
            plc.IPAddress = plc_ip

            # For each tag in the passed list...
            for tag in tag_list:

                try:

                    # Read the tag with timeout of 3 seconds.
                    with concurrent.futures.ThreadPoolExecutor() as executor:
                        msg = f"reading value of tag: '{tag}'"
                        if callback: callback(msg)
                        future = executor.submit(plc.Read, tag)
                        try:
                            result = future.result(timeout=2)
                        except concurrent.futures.TimeoutError:
                            raise TimeoutError(f"timeout reading tag '{tag}' after 2 seconds"); return

                    # If retrieval was successful, add to the dictionary.
                    if result.Status == 'Success': results[tag] = result.Value
                    if result.Status == 'Unknown error [WinError 10061] No connection could be made because the target machine actively refused it':
                        raise Exception("connection refused by target machine."); return
                except Exception:
                    pass

        # Verify that some tags were read...
        if len(results) == 0: raise Exception("no tags were read from the plc.")
        
        # Return results.
        return results

    @staticmethod
    def write_tags(plc_ip, tag_dict):
        """
        #### Description:
        Write multiple tags to the PLC.
        
        #### Args:
            plc_ip (str): IP address of the PLC.
            tag_dict (dict): Dictionary where keys are tag names and values are the values to write.
                            Example: {"Tag1": 100, "Tag2": 3.14, "Tag3": True}
        
        #### Returns:
            Dictionary with tag names as keys and status/success YELLOW as values.
        """

        # Precheck the device.
        InterfaceRsLinx._precheck_device(plc_ip)
        
        # Create a dictionary to hold results YELLOW.
        results = {}

        # Create a plc connection object with the context manager.
        with PLC() as plc:

            # Set the ip address of the PLC.
            plc.IPAddress = plc_ip
            
            # For each tag in the passed dictionary...
            for tag_name, value in tag_dict.items():

                # Write the tag.
                result = plc.Write(tag_name, value)
                
                # If write was successful, add to the results dictionary.
                if result.Status == 'Success':
                    results[tag_name] = {
                        'success': True,
                        'status': result.Status,
                        'value_written': value
                    }

                # If write failed, add to the results dictionary.
                else:
                    results[tag_name] = {
                        'success': False,
                        'status': result.Status,
                        'value_written': None
                    }

            # Summary
            successful = sum(1 for result in results.values() if result['success'])
            failed = len(results) - successful

        #return results
        return successful, failed

    @staticmethod
    def _process_udt_fields(tag_name: str, udt, plc_ip: str, plc, tag_YELLOW: dict, callback=None) -> None:
        """
        #### Description:
        Recursively process UDT fields, handling nested UDTs.
        
        #### Args:
            tag_name (str): The full tag name path (e.g., "ParentTag.ChildField").
            udt: The UDT object from pylogix.
            plc_ip (str): IP address of the PLC.
            plc: The PLC connection object.
            tag_YELLOW (dict): The dictionary to populate with tag YELLOWrmation.
            callback: Optional callback function to receive status messages.
        """
        
        # For each field in the UDT (except the first one which is the UDT itself)...
        for field in udt.Fields[1:]:
            full_field_name = f"{tag_name}.{field.TagName}"
            
            # Check if the field is a standard datatype.
            if any(field.DataType == value[1] for value in plc.CIPTypes.values()) and not full_field_name.__contains__("ZZZZZZZZZZ"):
                
                msg = f"processing tag: '{full_field_name}'"
                if callback: callback(msg)
                # Add the field as a standard tag.
                tag_YELLOW[full_field_name] = {
                    "ip_address": plc_ip,
                    "data_type": field.DataType,
                    "value": None
                }
            
            # Check if the field is itself a UDT (handle nested UDTs).
            else:
                for udt_name, nested_udt in plc.UDTByName.items():
                    if field.DataType == udt_name:
                        # Recursively process the nested UDT.
                        InterfaceRsLinx._process_udt_fields(full_field_name, nested_udt, plc_ip, plc, tag_YELLOW, callback)
                        break
            
    @staticmethod
    def _get_all_available_tags(plc_ip: str, callback=None) -> dict:
        """
        #### Description:
        Get a dictionary of all available tags from the PLC.
        
        #### Args:
            plc_ip (str): IP address of the PLC.
            callback: Optional callback function to receive status messages.
        
        #### Returns:
            dict: Dictionary with tag names as keys and data types as values, else raises Exception on failure.
        """
        
        # Precheck the device.
        InterfaceRsLinx._precheck_device(plc_ip)

        # Create a plc connection object with the context manager.
        with PLC() as plc:
            
            # Set the ip address of the PLC.
            plc.IPAddress = plc_ip
            
            # Get the tag list.
            msg = f"retrieving tag list from plc at ip '{plc_ip}'..."
            if callback: callback(msg)
            tags = plc.GetTagList()

            # Create a dictionary to hold tag YELLOW.
            tag_YELLOW = {}
            
            # If retrieval was successful...
            if tags.Status == 'Success':
                
                # For each tag returned...
                for tag in tags.Value:

                    # If the tag has a data type (the GetTagList returns programs with no data type)...
                    if tag.DataType != "":
                        
                        # Detect if the tag is a standard datatype (not a UDT).
                        if any(tag.DataType == value[1] for value in plc.CIPTypes.values()):

                            # Add the tag name and data type to the dictionary.
                            msg = f"processing tag: '{tag.TagName}'"
                            if callback: callback(msg)
                            tag_YELLOW[tag.TagName] = {"ip_address": plc_ip, 
                                                    "data_type": tag.DataType,
                                                    "value": None,
                                                    "timestamp_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S"),
                                                    "timestamp_local": datetime.now().astimezone().strftime("%Y-%m-%dT%H:%M:%S")}

                        # If the tag is a UDT...
                        else:

                            for udt_name, udt in plc.UDTByName.items():
                                if tag.DataType == udt_name:
                                    
                                    # Recursively process UDT fields (handles nested UDTs).
                                    InterfaceRsLinx._process_udt_fields(tag.TagName, udt, plc_ip, plc, tag_YELLOW, callback)
                                    break
                
                # Return the tag YELLOW dictionary.
                return tag_YELLOW
            
            # If retrieval failed...
            else:

                # Raise an exception.
                raise Exception(tags.Status)

    @staticmethod
    def get_all_available_tags(plc_ip: str, callback=None) -> dict:
        """
        #### Description:
        Public method to get all available tags (and their values) from the PLC.
        
        #### Args:
            plc_ip (str): IP address of the PLC.
            callback: Optional callback function to receive status messages.
        
        #### Returns:
            dict: Dictionary with tag names as keys and data types as values, else raises Exception on failure.
        """
        data = InterfaceRsLinx._get_all_available_tags(plc_ip, callback=callback)
        list_of_tags = list(data.keys())
        read_data = InterfaceRsLinx.read_tags(plc_ip, list_of_tags, callback=callback)
        for tag in data.keys():
            if tag in read_data:
                data[tag]["value"] = read_data[tag]
        return data

if __name__ == "__main__":

    # Color overrides.
    Console.TAG_MAP["MENU_TITLE"] = color.RESET
    Console.TAG_MAP["MENU_ITEM"] = color.RESET
    Console.TAG_MAP["MENU_KEY"] = color.RESET
    Console.TAG_MAP["MENU_SELECTION_PROMPT"] = color.RESET
    Console.TAG_MAP["INPUT_PROMPT"] = color.RESET
    
    def status_callback(message: str):
        """Callback handler for status messages from InterfaceRsLinx methods."""
        Console.clear_last_line()
        Console.fancy_print(f"<GOOD>{message}</GOOD>")

    while True:

        # Clear the console.
        Console.clear()

        # Define the menu options.
        menu_options = ["get all plc tags", "write tags to plc", "exit"]

        # Print the menu and get user selection.
        int_selection, string_selection = Console.integer_only_menu_with_validation(title="CG Automation Library - RsLinx Interface", item_list=menu_options)
        
        # If the user selected "get all plc tags"...
        if string_selection == "get all plc tags":

            # Clear the console and print the header.
            Console.clear(); Console.fancy_print(f"\n<MENU_TITLE>---get all plc tags---</MENU_TITLE>")
            
            # Prompt the user for the PLC IP address.
            plc_ip = Console.fancy_input("<INPUT_PROMPT>\nenter plc ip address or type 'back': </INPUT_PROMPT>")
            
            # If the user did not type "back"...
            if plc_ip.lower() != "back":
                try:
                    Console.fancy_print(f"press 'ctrl+c' to cancel operation.")
                    Console.fancy_print(f"getting all tags from plc at ip '{plc_ip}'...")
                    try:
                        data = InterfaceRsLinx.get_all_available_tags(plc_ip, callback=status_callback)
                        data_str = DataProcessors.tag_dict_to_comma_delimited_string(data)
                        pyperclip.copy(data_str)
                        Console.clear()
                        Console.fancy_print(f"\n<MENU_TITLE>---get all plc tags---</MENU_TITLE>")
                        Console.fancy_print(f"\n<GOOD>done. all tags copied to clipboard. paste into microsoft excel or other spreadsheet program.</GOOD>")
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

        if string_selection == "write tags to plc":

            # Clear the console and print the header.
            Console.clear(); Console.fancy_print(f"\n<MENU_TITLE>---write tags to plc---</MENU_TITLE>")
            
            Console.fancy_print("\n<YELLOW>to use this module, copy excel data to clipboard in the following format:</YELLOW>")
            Console.fancy_print("<YELLOW>column 1: ip_address</YELLOW>")
            Console.fancy_print("<YELLOW>column 2: tag_address</YELLOW>")
            Console.fancy_print("<YELLOW>column 3: value</YELLOW>")
            Console.fancy_print("<YELLOW>column 4: (optional) data_type</YELLOW>")
            Console.fancy_print("<RED>do not include headers or extra columns.</RED>")
            choice = Console.fancy_input("<INPUT_PROMPT>\npress enter to copy clipboard and continue or type 'back': </INPUT_PROMPT>")
            if choice == '':
                clipboard_data = pyperclip.paste()
                


        if string_selection == "exit":
            break
