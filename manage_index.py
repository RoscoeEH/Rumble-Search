from data_processing import get_index, ingest_files_to_index
from local_paths import RFC_PATH, MISC_PATH

class IndexWithData:
    def __init__(self, index, data):
        self.index = index
        self.data = data

    def update(self):
        ingest_files_to_index(self.index, self.data)

    def retrieve_index(self):
        return self.index


# Indexes
rfc_iwd = IndexWithData(
    get_index("rfc"),
    RFC_PATH
)
misc_iwd = IndexWithData(
    get_index("misc"),
    MISC_PATH
)


# maps a name to an index
INDEX_MAP = {
    "rfc": rfc_iwd,
    "misc": misc_iwd
}


def update_indexes():
    for name, index_obj in INDEX_MAP.items():
        index_obj.update()
