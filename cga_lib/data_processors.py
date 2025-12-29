class DataProcessors:

    @staticmethod
    def json_to_dict(file_path: str) -> dict:
        """
        #### Description:
        Read a JSON file and convert it to a dictionary.
        
        #### Args:
            file_path (str): Path to the JSON file.
        
        #### Returns:
            dict: Dictionary representation of the JSON file.
        """
        import json

        try:
            with open(file_path, 'r') as json_file:
                data_dict = json.load(json_file)
            return data_dict
        except Exception as e:
            raise Exception(f"error reading JSON file at '{file_path}': {e}")
        
    @staticmethod
    def tag_dict_to_comma_delimited_string(tag_dict: dict) -> str:
        """
        #### Description:
        Convert a dictionary of tags to a comma-delimited string with Excel-compatible newlines.
        
        #### Args:
            tag_dict (dict): Dictionary of tags.
        
        #### Returns:
            str: Comma-delimited string of tags with newlines.
        """
        try:
            tag_string = ''
            for tag, tag_value in tag_dict.items():
                tag_string += tag_value["ip_address"] + '\t'
                tag_string += tag + '\t'
                tag_string += str(tag_value["value"]) + '\t'
                tag_string += str(tag_value["data_type"]) + '\r\n'

            return tag_string
        except Exception as e:
            raise Exception(f"error converting tag dictionary to string: {e}")