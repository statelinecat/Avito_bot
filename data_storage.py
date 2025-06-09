import os

PRIVATE_SELLERS_FILE = "private_sellers.txt"
AGENCIES_FILE = "agencies.txt"
BUILDERS_FILE = "builders.txt"
NEGATIVE_RESPONSES_FILE = "negative_responses.txt"

def load_ids(file_path):
    if not os.path.exists(file_path):
        return set()
    with open(file_path, "r", encoding="utf-8") as file:
        return set(line.strip() for line in file)

def save_id(file_path, item_id):
    with open(file_path, "a", encoding="utf-8") as file:
        file.write(f"{item_id}\n")