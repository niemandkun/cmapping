ERROR_MSG = 'Expected list of length less or equal to {array_len},\
but was {length}.'


def padded_with_zeros(_list, length):
    ''' Returns list padded with zeroes at the end to match length. '''
    if len(_list) > length:
        raise ValueError(ERROR_MSG.format(length=length,
                                          array_len=len(_list)))
    return list(_list) + [0,] * (length - len(_list))
