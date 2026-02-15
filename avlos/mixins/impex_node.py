class ImpexNode:
    def import_values(self, data):
        try:
            if "export" in self.meta and self.meta["export"] == True:
                if isinstance(data, str):
                    self.set_value_with_string(data)
                else:
                    self.set_value(data)
        except AttributeError:
            for name, attr in self.remote_attributes.items():
                try:
                    if name in data:
                        attr.import_values(data[name])
                except AttributeError:
                    pass

    def export_values(self):
        try:
            if "export" in self.meta and self.meta["export"] == True:
                return self.get_value()
        except AttributeError:
            values = {}
            for name, node in self.remote_attributes.items():
                try:
                    val = node.export_values()
                    if val != None:
                        values[name] = val
                except AttributeError:
                    pass
            if len(values) > 0:
                return values
            return None
