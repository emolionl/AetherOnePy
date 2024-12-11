import os
import sys
import json

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from domains.aetherOneDomains import Catalog, Rate
from services.databaseService import get_case_dao

aetherOneDB = get_case_dao('../../data/aetherone.db')

class RateImporter:
    def generate_folder_file_json(self, rootFolder):
        result = {"folders": {}}

        for dirpath, dirnames, filenames in os.walk(rootFolder):
            folder_name = os.path.basename(dirpath)
            txt_files = [f for f in filenames if f.endswith('.txt')]
            if txt_files:
                result["folders"][folder_name] = txt_files

        return json.dumps(result, indent=2)

    def find_file_path(self, root_folder, file_name):
        """Search for the file in subfolders and return its full path."""
        for dirpath, dirnames, filenames in os.walk(root_folder):
            if file_name in filenames:
                return os.path.join(dirpath, file_name)
        return None

    def import_file(self, root_folder, file_name):
        file_path = self.find_file_path(root_folder, file_name)
        if not file_path:
            print(f"File '{file_name}' not found in '{root_folder}'.")
            return

        # Read and process the file
        with open(file_path, 'r', encoding='utf-8') as file:
            lines = file.readlines()

        catalog_name = os.path.splitext(file_name)[0]
        try:
            # Insert the catalog
            catalog = aetherOneDB.get_catalog_by_name(catalog_name)
            if catalog is None:
                aetherOneDB.insert_catalog(Catalog(catalog_name, 'radionics-rates', '-'))
                catalog = aetherOneDB.get_catalog_by_name(catalog_name)
            else:
                print(f"Warning: catalog '{catalog_name}' already exists.")
                return

            if not catalog:
                print(f"Error: Unable to retrieve catalog '{catalog_name}' after insertion.")
                return

            # Insert rates
            for idx, line in enumerate(lines):
                line = line.strip()
                if line:  # Ignore empty lines
                    try:
                        signature, *description = line.split('\t', 1)
                        description = description[0] if description else None
                        aetherOneDB.insert_rate(Rate(signature, description, catalog.id))
                    except ValueError as e:
                        print(f"Error processing line {idx + 1}: '{line}' - {e}")

            print(f"File '{file_name}' imported successfully.")
        except Exception as e:
            print(f"Error importing file '{file_name}': {e}")

if __name__ == '__main__':
    rateImporter = RateImporter()
    # Generate and print folder structure JSON
    json_result = rateImporter.generate_folder_file_json('../../data/radionics-rates')
    print(json_result)

    # Import a specific file
    rateImporter.import_file('../../data/radionics-rates', 'HOMEOPATHY_Clarke_With_MateriaMedicaUrls.txt')
