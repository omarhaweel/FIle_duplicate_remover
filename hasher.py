import hashlib
import os
from collections import defaultdict

class Hasher:
    def __init__(self, chunk_size):
        self.chunk_size = chunk_size
    
    def hash_file(self, file_path):
        sha256 = hashlib.sha256()
        try:
            with open(file_path, 'rb') as f:
                while chunk := f.read(self.chunk_size):
                    sha256.update(chunk)
        except FileNotFoundError:
            print(f"File not found: {file_path}")
        except Exception as e:
            print(f"Error reading file: {e}")
        return sha256.hexdigest()
    
    def find_duplicates_on_size(self, main_directory, extension):
        size_dict = {}
        duplicates = []

        try:
            for root, _, files in os.walk(main_directory):
                for file in files:
                    if not any(file.lower().endswith(ext) for ext in extension):
                        continue
                    file_path = os.path.join(root, file)
                    if not os.path.isfile(file_path):
                        continue
                    size = os.path.getsize(file_path)
                    if size not in size_dict:
                        size_dict[size] = []
                    size_dict[size].append(file_path)


            duplicates = [group for group in size_dict.values() if len(group) > 1]
        except Exception as e:
            print(f"Error while finding duplicates: {e}")
        return duplicates

    
    def hash_duplicates(self, duplicates):
        hash_dict = defaultdict(list)
        for group in duplicates:
            for file_path in group:
                file_hash = self.hash_file(file_path)
                hash_dict[file_hash].append(file_path)

        return [group for group in hash_dict.values() if len(group) > 1]
    
    def remove_duplicates(self, main_directory):
        duplicates_on_size = self.find_duplicates_on_size(main_directory)
        duplicates_on_hash = self.hash_duplicates(duplicates_on_size)

        removed_files = []
        for group in duplicates_on_hash:
            for file_path in group[1:]:
                try:
                    os.remove(file_path)
                    removed_files.append(file_path)
                except Exception as e:
                    print(f"Error removing file {file_path}: {e}")
        if removed_files:
            return len(removed_files), removed_files
        else:
            print("No duplicates found.")
            return 0, []



