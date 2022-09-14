def _raiser(cond, excpt, err_msg):
    if cond:
        raise excpt(err_msg)


def raise_for_not_put_in_a_container(ipt, excpt, err_msg):
    try:
        iter(ipt)
    except TypeError as te:
        raise excpt(err_msg)

    cond = isinstance(ipt, str)
    _raiser(cond, excpt, err_msg)
