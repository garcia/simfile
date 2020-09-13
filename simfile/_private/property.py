def attr_property(private_name):

    @property
    def chart_property(self):
        return getattr(self, private_name)

    @chart_property.setter
    def chart_property(self, value):
        setattr(self, private_name, value)

    return chart_property

def item_property(name):

    @property
    def chart_property(self):
        return self[name]

    @chart_property.setter
    def chart_property(self, value):
        self[name] = value

    return chart_property