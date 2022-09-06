from ansa import base, constants


def create_and_get_shell():
    deck = constants.LSDYNA
    type_ = 'SECTION_SHELL'
    shell = base.CreateEntity(deck, type_, {'PID': 1})
    print(f'{shell=}')

    got_shell1 = base.GetEntity(deck, type_,  1)
    print(f'{got_shell1=}')

    type_ = '__PROPERTIES__'
    got_shell2 = base.GetEntity(deck, type_,  1)
    print(f'{got_shell2=}')


if __name__ == '__main__':
    create_and_get_shell()
