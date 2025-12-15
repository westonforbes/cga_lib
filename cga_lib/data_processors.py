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