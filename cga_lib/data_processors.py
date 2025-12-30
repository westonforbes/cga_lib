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
    def tag_dict_to_tab_delimited_string(tag_dict: dict) -> str:
        """
        #### Description:
        Convert a dictionary of tags to a tab-delimited string with Excel-compatible newlines.
        
        #### Args:
            tag_dict (dict): Dictionary of tags.
        
        #### Returns:
            str: Tab-delimited string of tags with newlines.
        """
        try:
            tag_string = ''
            for tag, tag_value in tag_dict.items():
                tag_string += tag_value["ip_address"] + '\t'
                tag_string += tag + '\t'
                tag_string += str(tag_value["value"]) + '\t'
                tag_string += str(tag_value["data_type"]) + '\n'

            return tag_string
        except Exception as e:
            raise Exception(f"error converting tag dictionary to string: {e}")
        
    @staticmethod
    def save_tags_to_csv(content: str, file_path: str) -> None:
        """
        #### Description:
        Convert a tab-delimited string to a CSV file.
        
        #### Args:
            content (str): Tab-delimited string with \\n line endings.
            file_path (str): Path where the CSV file will be written.
        
        #### Returns:
            None
        """
        try:
            content = content.replace('\t', ',')
            with open(file_path, 'w', newline='') as csv_file:
                csv_file.write(content)
        except Exception as e:
            raise Exception(f"error writing csv file to '{file_path}': {e}")