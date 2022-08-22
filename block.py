


class Singleline_block(AbstractCompositeItem):
    key = "*SINGLEINEDATABLOCK"
    dataclass = Singleline

    def __init__(self, datalines):
        super(Singleline_block, self).__init__(datalines)

    def to_str(self):
        stringed_key = self.key
        stringed_children = "\n".join([x.to_str() for x in self])
        return stringed_key + "\n" + stringed_children

    def to_dict(self):
        return [x.to_dict() for x in self]

    @classmethod
    def from_lines(cls, lines):
        datalines = [cls.dataclass.from_str(x) for x in lines]
        return cls(datalines)


class Multiline_block(AbstractCompositeItem):
    key = "*MULTILINEDATABLOCK"
    dataclass = Multiline

    def __init__(self, datalines):
        super(Multiline_block, self).__init__(datalines)

    def to_str(self):
        stringed_key = self.key
        stringed_children = "\n".join([x.to_str() for x in self])
        return stringed_key + "\n" + stringed_children

    def to_dict(self):
        return [x.to_dict() for x in self]