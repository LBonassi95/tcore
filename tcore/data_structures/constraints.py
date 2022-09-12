ALWAYS = 'always'
SOMETIME = 'sometime'
ATMOSTONCE = 'at-most-once'
SOMETIMEBEFORE = 'sometime-before'
SOMETIMEAFTER = 'sometime-after'

KINDS = [ALWAYS, SOMETIME, ATMOSTONCE, SOMETIMEAFTER, SOMETIMEBEFORE]


def has2gd(kind):
    return kind == SOMETIMEAFTER or kind == SOMETIMEBEFORE


class HardConstraint:
    def __init__(self, condition, kind):
        self.gd1 = condition
        self.kind = kind
        self.monitoring_atom = ''

    def __eq__(self, other):
        return (self.__class__ == other.__class__ and
                self.gd1 == other.gd1)

    def set_monitoring_atom_predicate(self, predicate):
        self.monitoring_atom = predicate

    def __str__(self):
        return f'({self.kind} {str(self.gd1)})'

    def __repr__(self) -> str:
        return str(self)


class Always(HardConstraint):
    def __init__(self, condition):
        super().__init__(condition, ALWAYS)


class Sometime(HardConstraint):
    def __init__(self, condition):
        super().__init__(condition, SOMETIME)


class AtMostOnce(HardConstraint):
    def __init__(self, condition):
        super().__init__(condition, ATMOSTONCE)


class SometimeBefore(HardConstraint):
    def __init__(self, condition1, condition2):
        super().__init__(condition1, SOMETIMEBEFORE)
        self.gd2 = condition2

    def __eq__(self, other):
        return (self.__class__ == other.__class__ and
                self.gd1 == other.gd1 and self.gd2 == other.gd2)

    def __str__(self):
        return f'({self.kind} {str(self.gd1)} {str(self.gd2)})'


class SometimeAfter(HardConstraint):
    def __init__(self, condition1, condition2):
        super().__init__(condition1, SOMETIMEAFTER)
        self.gd2 = condition2

    def __eq__(self, other):
        return (self.__class__ == other.__class__ and
                self.gd1 == other.gd1 and self.gd2 == other.gd2)

    def __str__(self):
        return f'({self.kind} {str(self.gd1)} {str(self.gd2)})'
