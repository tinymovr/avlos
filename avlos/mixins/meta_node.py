class MetaNode:
    def __init__(self, meta_dict):
        self.meta_dict = meta_dict

    @property
    def meta(self):
        return self.meta_dict
