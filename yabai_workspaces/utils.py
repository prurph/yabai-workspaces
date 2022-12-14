from __future__ import annotations

from collections import OrderedDict
from collections.abc import Callable, Iterable
from itertools import filterfalse, tee
from typing import TYPE_CHECKING, List, OrderedDict, Tuple, TypeVar

if TYPE_CHECKING:
    from _typeshed import SupportsRichComparison

    _T = TypeVar("_T")
    _S = TypeVar("_S", bound=SupportsRichComparison)
    _R = TypeVar("_R", bound=SupportsRichComparison)


def ordered_groupby(
    iter: Iterable[_T], sortkeyby: Callable[[_T], _S], sortvaluesby: Callable[[_T], _R]
) -> OrderedDict[_S, List[_T]]:
    """Group elements of an iterator into a dict with ordered keys and values."""
    ret: OrderedDict[_S, List[_T]] = OrderedDict()
    for el in sorted(iter, key=lambda x: (sortkeyby(x), sortvaluesby(x))):
        ret.setdefault(sortkeyby(el), []).append(el)
    return ret


# Typed version of https://docs.python.org/3/library/itertools.html#itertools-recipes
def partition(
    pred: Callable[[_T], bool], iterable: Iterable[_T]
) -> Tuple[List[_T], List[_T]]:
    t1, t2 = tee(iterable)
    return (list(filterfalse(pred, t1)), list(filter(pred, t2)))
