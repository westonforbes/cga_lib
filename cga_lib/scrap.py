                        # Detect if the tag is a UDT.
                        if not any(tag.DataType == value[1] for value in plc.CIPTypes.values()):
                            udt_data = plc._get_program_tag_list(tag.TagName)
                            print("")

                        # Access UDT structure
                        for udt_name, udt in plc.UDTByName.items():
                            print(f"UDT: {udt_name}")
                            for field in udt.Fields:
                                print(f"  - {field.TagName}: {field.DataType}")