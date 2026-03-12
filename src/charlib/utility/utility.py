import numpy as np
import QuantLib as ql
from charlib.curves import conventions, pricingobjects, swaps


def create_pricing_object_from_convention(start_date, end_date, notional, this_convention):
    if isinstance(this_convention, str):
        this_convention = conventions.all_conventions[this_convention]

    if this_convention['type'] in (swaps.VanillaSwap, swaps.TermBasisSwap):
        return create_swap_from_convention(start_date, end_date, notional, this_convention)
    else:
        return pricingobjects.ForwardRate(
            start_date,
            end_date,
            this_convention['curves_bindings'],
        )


def create_swap_from_convention(start_date, end_date, notional, this_convention):
    if isinstance(this_convention, str):
        this_convention = conventions.all_conventions[this_convention]

    return this_convention['type'](
        start_date,
        end_date,
        this_convention['ccy'],
        notional,
        this_convention['left_leg'],
        this_convention['right_leg'],
        this_convention['curves_bindings'],
    )


def create_constraint(arr):
    if isinstance(arr, (list, tuple, np.ndarray)):
        if len(arr) == 2:
            return pricingobjects.Spread(arr[0], arr[1])
        elif len(arr) == 3:
            return pricingobjects.Fly(arr[0], arr[1], arr[2])
        else:
            raise ValueError(
                f"Contraint must be an array of size 2 for a spread or size 3 for a fly; got {len(arr)}"
            )
    else:
        raise TypeError(
            f"Contraint must be an array of size 2 for a spread or size 3 for a fly; got {type(arr).__name__}"
        )


def hello():
    print('hello')