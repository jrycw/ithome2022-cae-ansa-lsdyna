from ansa import base, constants


def name_to_ents():
    deck = constants.LSDYNA
    set1 = base.CreateEntity(deck, 'SET', {'Name': 'SET1'})
    set2 = base.CreateEntity(deck, 'SET', {'Name': 'SET2'})

    sets1 = base.NameToEnts('SET', deck=deck, match=constants.ENM_SUBSTRING)
    print(f'{sets1=}')

    sets2 = base.NameToEnts('set', deck=deck, match=constants.ENM_SUBSTRING)
    print(f'{sets2=}')

    sets3 = base.NameToEnts(
        'set', deck=deck, match=constants.ENM_SUBSTRING_IGNORECASE)
    print(f'{sets3=}')


if __name__ == '__main__':
    name_to_ents()
