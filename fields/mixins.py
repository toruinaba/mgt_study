class Mixin_base(object):
    def __init__(self):
        raise NotImplementedError("Mixin class cannot create instance.")


class ElementMixin(object):
    @property
    def node_ids(self):
        raise NotImplementedError

    @property
    def is_line(self):
        return len(self.node_ids) == 2

    @property
    def is_triangle(self):
        return len(self.node_ids) == 3

    @property
    def is_quad(self):
        return len(self.node_ids) == 4

    def search_coordinates(self, node):
        return tuple([node[x].coordinate for x in self.node_ids])

