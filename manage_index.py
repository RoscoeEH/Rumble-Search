from data_processing import get_index, ingest_files_to_index


class IndexWithData:
    def __init__(self, index, data):
        self.index = index
        self.data = data

    def update(self):
        ingest_files_to_index(self.index, self.data)

    def retrieve_index(self):
        return self.index

# Indexes
misc_iwd = IndexWithData(
    get_index("misc"),
    "./data/misc")



# maps a name to an index
INDEX_MAP = {
    "misc" : misc_iwd
}

def update_indexes():
    for name in INDEX_MAP.keys():
        INDEX_MAP[name].update()
