import typing


class Typex:
    class TypexVariable:
        def __init__(self, name):
            self.name = name

        def __str__(self):
            return '`' + self.name

        def __repr__(self):
            return str(self)

    def __init__(self, structs: typing.Sequence[typing.Union['Typex', TypexVariable, str]]):
        self.structs = structs

    def __str__(self):
        return '[' + ' '.join([str(i) for i in self.structs]) + ']'

    def __repr__(self):
        return str(self)


def typex_variable_names_impl(a, ret: typing.MutableSet[str]):
    if isinstance(a, str):
        pass
    elif isinstance(a, Typex):
        for sub in a.structs:
            typex_variable_names_impl(sub, ret)
    elif isinstance(a, Typex.TypexVariable):
        ret.add(a.name)
    else:
        raise ValueError()


def typex_variable_names(a):
    ret = set()
    typex_variable_names_impl(a, ret)
    return ret


def typex_copy(a):
    if isinstance(a, str):
        return a
    elif isinstance(a, Typex):
        return Typex([typex_copy(i) for i in a.structs])
    elif isinstance(a, Typex.TypexVariable):
        return Typex.TypexVariable(a.name)
    else:
        return None


def typex_rename_used_variable(a, used_set: typing.Collection[str], name_mapping: typing.MutableMapping[str, str]):
    if isinstance(a, str):
        return a
    elif isinstance(a, Typex):
        return Typex([typex_rename_used_variable(i, used_set, name_mapping) for i in a.structs])
    elif isinstance(a, Typex.TypexVariable):
        new_name = a.name
        if name_mapping.get(new_name, None):
            new_name = name_mapping[new_name]
        else:
            while new_name in used_set:
                new_name = new_name + '_'
            name_mapping[a.name] = new_name

        return Typex.TypexVariable(new_name)


def typex_rename_variable(a, src: str, dst: str):
    if isinstance(a, str):
        pass
    elif isinstance(a, Typex):
        for i in a.structs:
            typex_rename_variable(i, src, dst)
    elif isinstance(a, Typex.TypexVariable):
        if a.name == src:
            a.name = dst


tx_ty = typing.Union[Typex, Typex.TypexVariable, str]
av_ty = typing.MutableMapping[str, tx_ty]


def typex_get(a, assigned_variables: av_ty):
    if isinstance(a, Typex.TypexVariable):
        return assigned_variables[a.name]
    else:
        return a


def typex_apply_assigned_variables(a, assigned_variables: av_ty):
    if isinstance(a, str):
        return a
    elif isinstance(a, Typex):
        return Typex([typex_apply_assigned_variables(i, assigned_variables) for i in a.structs])
    elif isinstance(a, Typex.TypexVariable):
        if a.name in assigned_variables:
            return typex_apply_assigned_variables(assigned_variables[a.name], assigned_variables)
        else:
            return typex_copy(a)
    else:
        raise ValueError()


def typex_meet_impl(a, b, assigned_variables: av_ty, merge_variables: typing.Callable[[str, str], None]):
    if isinstance(a, str):
        if isinstance(b, str):
            if a == b:
                return a
            else:
                return None
        elif isinstance(b, Typex):
            return None
        elif isinstance(b, Typex.TypexVariable):
            if assigned_variables.get(b.name, None):
                if a == assigned_variables[b.name]:
                    return a
                else:
                    return None
            else:
                assigned_variables[b.name] = a
                return a
        else:
            return None
    elif isinstance(a, Typex):
        if isinstance(b, str):
            return None
        elif isinstance(b, Typex):
            structures = [typex_meet_impl(ia, ib, assigned_variables, merge_variables) for ia, ib in
                          zip(a.structs, b.structs)]
            if None in structures:
                return None
            else:
                return Typex(structures)
        elif isinstance(b, Typex.TypexVariable):
            if assigned_variables.get(b.name, None):
                return typex_meet_impl(assigned_variables[b.name], a, assigned_variables, merge_variables)
            else:
                assigned_variables[b.name] = typex_copy(a)
                return assigned_variables[b.name]
        else:
            return None
    elif isinstance(a, Typex.TypexVariable):
        if isinstance(b, str):
            if assigned_variables.get(a.name, None):
                if assigned_variables[a.name] == b:
                    return b
                else:
                    return None
            else:
                assigned_variables[a.name] = b
                return b
        elif isinstance(b, Typex):
            if assigned_variables.get(a.name, None):
                return typex_meet_impl(assigned_variables[a.name], b, assigned_variables, merge_variables)
            else:
                assigned_variables[a] = typex_copy(b)
                return assigned_variables[a.name]
        elif isinstance(b, Typex.TypexVariable):
            if assigned_variables.get(a.name, None):
                merge_variables(b.name, a.name)
                return typex_copy(a)
            else:
                merge_variables(a.name, b.name)
                return typex_copy(a)
        else:
            return None
    else:
        return None


def typex_meet(a, b):
    b = typex_rename_used_variable(b, typex_variable_names(a), {})

    def merge_variables(va, vb):
        typex_rename_variable(b, vb, va)

    av = {}
    ret = typex_meet_impl(a, b, av, merge_variables)
    print(str(av))
    ret = typex_apply_assigned_variables(a, av)
    return ret


def main():
    print(typex_meet('A', Typex.TypexVariable('a')))
    print(typex_meet(
        Typex(['list', '32', Typex.TypexVariable('ty')]),
        Typex(['list', Typex.TypexVariable('len'), 'float'])
    ))
    print(typex_meet(
        Typex([
            Typex(['list', '32', Typex.TypexVariable('ty')]),
            Typex(['list', Typex.TypexVariable('len'), 'float'])
        ]),
        Typex([Typex.TypexVariable('a'), Typex.TypexVariable('a')])
    ))


if __name__ == '__main__':
    main()
