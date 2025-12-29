import re
from pylogix import PLC
from datetime import datetime, timezone
import concurrent.futures
from ping3 import ping

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
    def read_tags(plc_ip: str, tag_list: list[str]) -> dict:
        """
        #### Description:
        Read tags from the PLC.
        
        #### Args:
            plc_ip (str): IP address of the PLC.
            tag_list (list): List of tag names to read.
        
        #### Returns:
            Dictionary with tag names as keys and values.
        """

        # Precheck the device.
        InterfaceRsLinx._precheck_device(plc_ip)

        # Create a dictionary to hold results info.
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
                        future = executor.submit(plc.Read, tag)
                        try:
                            result = future.result(timeout=2)
                        except concurrent.futures.TimeoutError:
                            raise TimeoutError(f"Timeout reading tag '{tag}' after 2 seconds"); return

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
            Dictionary with tag names as keys and status/success info as values.
        """

        # Precheck the device.
        InterfaceRsLinx._precheck_device(plc_ip)
        
        # Create a dictionary to hold results info.
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
    def get_all_available_tags(plc_ip: str) -> dict:
        """
        #### Description:
        Get a dictionary of all available tags from the PLC.
        
        #### Args:
            plc_ip (str): IP address of the PLC.
        
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
            tags = plc.GetTagList()

            # Create a dictionary to hold tag info.
            tag_info = {}
            
            # If retrieval was successful...
            if tags.Status == 'Success':

                # For each tag returned...
                for tag in tags.Value:

                    # If the tag has a data type (the GetTagList returns programs with no data type)...
                    if tag.DataType != "":
                        
                        # Detect if the tag is a standard datatype (not a UDT).
                        if any(tag.DataType == value[1] for value in plc.CIPTypes.values()):

                            # Add the tag name and data type to the dictionary.
                            tag_info[tag.TagName] = {"ip_address": plc_ip, 
                                                    "data_type": tag.DataType,
                                                    "value": None,
                                                    "timestamp_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S"),
                                                    "timestamp_local": datetime.now().astimezone().strftime("%Y-%m-%dT%H:%M:%S")}
                        
                        # If the tag is a UDT...
                        else:

                            for udt_name, udt in plc.UDTByName.items():
                                if tag.DataType == udt_name:
                                    
                                    # Create a dictionary to hold UDT fields.
                                    udt_fields = {}

                                    # For each field in the UDT (except the first one which is the UDT itself)...
                                    for field in udt.Fields[1:]:
                                        tag_info[f"{tag.TagName}.{field.TagName}"] = {"ip_address": plc_ip, 
                                                            "data_type": tag.DataType,
                                                            "udt_fields": udt_fields,
                                                            "value": None,
                                                            "timestamp_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S"),
                                                            "timestamp_local": datetime.now().astimezone().strftime("%Y-%m-%dT%H:%M:%S")}

                
                # Return the tag info dictionary.
                return tag_info
            
            # If retrieval failed...
            else:

                # Raise an exception.
                raise Exception(tags.Status)


if __name__ == "__main__":
    data = InterfaceRsLinx.get_all_available_tags("191.191.191.9")
    list_of_tags = list(data.keys())
    read_data = InterfaceRsLinx.read_tags("191.191.191.9", list_of_tags)
    for tag in data.keys():
        if tag in read_data:
            data[tag]["value"] = read_data[tag]
    
    import json
    print(json.dumps(data, indent=4))