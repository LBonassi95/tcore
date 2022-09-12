
class Formula:
    def __init__(self, components):
        self.components = components

    def __eq__(self, other):
        if self.__class__ == other.__class__:
            if len(self.components) == len(other.components):
                for i in range(len(self.components)):
                    if self.components[i] != other.components[i]:
                        return False
                return True
            else:
                return False
        else:
            return False
    
    def __repr__(self) -> str:
        return str(self)


class Or(Formula):

    def __str__(self):
        components_str = ''
        for disjunct in self.components:
            components_str += str(disjunct)
        return '(or {})'.format(components_str)

    def negate(self):
        new_components = [comp.negate() for comp in self.components]
        return And(new_components)

    def simplified(self):
        new_components = []
        for component in self.components:
            son_simplified = component.simplified()
            if isinstance(son_simplified, And):
                new_components.append(son_simplified)
            elif isinstance(son_simplified, Or):
                new_components += [conjunct for conjunct in son_simplified.components]
            elif isinstance(son_simplified, Literal):
                new_components.append(son_simplified)
            elif isinstance(son_simplified, TRUE):
                return TRUE()
        if len(new_components) == 0:
            return FALSE()
        elif len(new_components) == 1:
            return new_components[0]
        else:
            return Or(new_components)


class And(Formula):

    def __str__(self):
        components_str = ''
        for disjunct in self.components:
            components_str += str(disjunct)
        return '(and {})'.format(components_str)

    def negate(self):
        new_components = [comp.negate() for comp in self.components]
        return Or(new_components)

    def simplified(self):
        new_components = []
        for component in self.components:
            son_simplified = component.simplified()
            if isinstance(son_simplified, And):
                new_components += [conjunct for conjunct in son_simplified.components]
            elif isinstance(son_simplified, Or):
                new_components.append(son_simplified)
            elif isinstance(son_simplified, Literal):
                new_components.append(son_simplified)
            elif isinstance(son_simplified, FALSE):
                return FALSE()
        if len(new_components) == 0:
            return TRUE()
        elif len(new_components) == 1:
            return new_components[0]
        else:
            return And(new_components)


class Literal:
    def __init__(self, lit, negated):
        self.literal = lit
        self.negated = negated

    def __str__(self):
        if self.negated:
            return '(not ({}))'.format(self.literal)
        else:
            return '({})'.format(self.literal)

    def negate(self):
        return Literal(self.literal, not self.negated)

    def __eq__(self, other):
        return self.__class__ == other.__class__ and \
               self.literal == other.literal and \
               self.negated == other.negated

    def simplified(self):
        return Literal(self.literal, self.negated)

    def __hash__(self) -> int:
        return hash((self.literal, self.negated))

    def __repr__(self) -> str:
        return str(self)


class TRUE:

    def __init__(self):
        pass

    def __eq__(self, other):
        return self.__class__ == other.__class__

    def simplified(self):
        return TRUE()

    def __str__(self):
        return '(TRUE)'

    def negate(self):
        return FALSE()
    
    def __repr__(self) -> str:
        return str(self)


class FALSE:

    def __init__(self):
        pass

    def __eq__(self, other):
        return self.__class__ == other.__class__

    def simplified(self):
        return FALSE()

    def __str__(self):
        return '(FALSE)'

    def negate(self):
        return TRUE()
    
    def __repr__(self) -> str:
        return str(self)
