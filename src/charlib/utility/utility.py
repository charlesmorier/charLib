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


imm_dates = [
    ql.Date(17, 12, 2025),
    ql.Date(18, 3, 2026),
    ql.Date(17, 6, 2026),
    ql.Date(16, 9, 2026),
    ql.Date(16, 12, 2026),
    ql.Date(17, 3, 2027),
    ql.Date(16, 6, 2027),
    ql.Date(15, 9, 2027),
    ql.Date(15, 12, 2027),
    ql.Date(15, 3, 2028),
    ql.Date(21, 6, 2028),
    ql.Date(20, 9, 2028),
    ql.Date(20, 12, 2028),
    ql.Date(21, 3, 2029),
    ql.Date(20, 6, 2029),
    ql.Date(19, 9, 2029),
    ql.Date(19, 12, 2029),
    ql.Date(20, 3, 2030),
    ql.Date(20, 6, 2030),
    ql.Date(18, 9, 2030),
    ql.Date(18, 12, 2030),
    ql.Date(19, 3, 2031),
    ql.Date(18, 6, 2031),
    ql.Date(17, 9, 2031),
    ql.Date(17, 12, 2031),
    ql.Date(17, 3, 2032),
    ql.Date(16, 6, 2032),
    ql.Date(15, 9, 2032),
    ql.Date(15, 12, 2032),
    ql.Date(16, 3, 2033),
    ql.Date(15, 6, 2033),
    ql.Date(21, 9, 2033),
    ql.Date(21, 12, 2033),
    ql.Date(15, 3, 2034),
    ql.Date(21, 6, 2034),
    ql.Date(20, 9, 2034),
    ql.Date(20, 12, 2034),
    ql.Date(21, 3, 2035),
    ql.Date(20, 6, 2035),
    ql.Date(19, 9, 2035),
]


def get_imm_contract(this_date):
    imm_codes = {3: "H", 6: "M", 9: "U", 12: "Z"}
    return imm_codes[this_date.month()] + str(this_date.year() - 2000)


imm_dates = {
    'Z25': ql.Date(17, 12, 2025),
    'H26': ql.Date(18, 3, 2026),
    'M26': ql.Date(17, 6, 2026),
    'U26': ql.Date(16, 9, 2026),
    'Z26': ql.Date(16, 12, 2026),
    'H27': ql.Date(17, 3, 2027),
    'M27': ql.Date(16, 6, 2027),
    'U27': ql.Date(15, 9, 2027),
    'Z27': ql.Date(15, 12, 2027),
    'H28': ql.Date(15, 3, 2028),
    'M28': ql.Date(21, 6, 2028),
    'U28': ql.Date(20, 9, 2028),
    'Z28': ql.Date(20, 12, 2028),
    'H29': ql.Date(21, 3, 2029),
    'M29': ql.Date(20, 6, 2029),
    'U29': ql.Date(19, 9, 2029),
    'Z29': ql.Date(19, 12, 2029),
    'H30': ql.Date(20, 3, 2030),
    'M30': ql.Date(20, 6, 2030),
    'U30': ql.Date(18, 9, 2030),
    'Z30': ql.Date(18, 12, 2030),
    'H31': ql.Date(19, 3, 2031),
    'M31': ql.Date(18, 6, 2031),
    'U31': ql.Date(17, 9, 2031),
    'Z31': ql.Date(17, 12, 2031),
    'H32': ql.Date(17, 3, 2032),
    'M32': ql.Date(16, 6, 2032),
    'U32': ql.Date(15, 9, 2032),
    'Z32': ql.Date(15, 12, 2032),
    'H33': ql.Date(16, 3, 2033),
    'M33': ql.Date(15, 6, 2033),
    'U33': ql.Date(21, 9, 2033),
    'Z33': ql.Date(21, 12, 2033),
    'H34': ql.Date(15, 3, 2034),
    'M34': ql.Date(21, 6, 2034),
    'U34': ql.Date(20, 9, 2034),
    'Z34': ql.Date(20, 12, 2034),
    'H35': ql.Date(21, 3, 2035),
    'M35': ql.Date(20, 6, 2035),
    'U35': ql.Date(19, 9, 2035),
}

sfe_au_dates = {
    'Z25': ql.Date(11, 12, 2025),
    'H26': ql.Date(12, 3, 2026),
    'M26': ql.Date(11, 6, 2026),
    'U26': ql.Date(10, 9, 2026),
    'Z26': ql.Date(10, 12, 2026),
    'H27': ql.Date(11, 3, 2027),
    'M27': ql.Date(10, 6, 2027),
    'U27': ql.Date(9, 9, 2027),
    'Z27': ql.Date(9, 12, 2027),
    'H28': ql.Date(9, 3, 2028),
    'M28': ql.Date(8, 6, 2028),
    'U28': ql.Date(7, 9, 2028),
    'Z28': ql.Date(7, 12, 2028),
    'H29': ql.Date(8, 3, 2029),
    'M29': ql.Date(7, 6, 2029),
    'U29': ql.Date(13, 9, 2029),
    'Z29': ql.Date(13, 12, 2029),
    'H30': ql.Date(7, 3, 2030),
    'M30': ql.Date(13, 6, 2030),
    'U30': ql.Date(12, 9, 2030),
    'Z30': ql.Date(12, 12, 2030),
    'H31': ql.Date(13, 3, 2031),
    'M31': ql.Date(12, 6, 2031),
    'U31': ql.Date(11, 9, 2031),
    'Z31': ql.Date(11, 12, 2031),
    'H32': ql.Date(11, 3, 2032),
    'M32': ql.Date(10, 6, 2032),
    'U32': ql.Date(9, 9, 2032),
    'Z32': ql.Date(9, 12, 2032),
    'H33': ql.Date(10, 3, 2033),
    'M33': ql.Date(9, 6, 2033),
    'U33': ql.Date(8, 9, 2033),
    'Z33': ql.Date(8, 12, 2033),
    'H34': ql.Date(9, 3, 2034),
    'M34': ql.Date(8, 6, 2034),
    'U34': ql.Date(7, 9, 2034),
    'Z34': ql.Date(7, 12, 2034),
    'H35': ql.Date(8, 3, 2035),
    'M35': ql.Date(7, 6, 2035),
    'U35': ql.Date(13, 9, 2035),
    'Z35': ql.Date(13, 12, 2035),
}

rba_dates = {
    'Dec25': ql.Date(10, 12, 2025),
    'Feb26': ql.Date(4, 2, 2026),
    'Mar26': ql.Date(18, 3, 2026),
    'May26': ql.Date(6, 5, 2026),
    'Jun26': ql.Date(17, 6, 2026),
    'Aug26': ql.Date(12, 8, 2026),
    'Sep26': ql.Date(30, 9, 2026),
    'Nov26': ql.Date(4, 11, 2026),
    'Dec26': ql.Date(9, 12, 2026),
    'Feb27': ql.Date(3, 2, 2027),
    'Mar27': ql.Date(17, 3, 2027),
    'May27': ql.Date(5, 5, 2027),
    'Jun27': ql.Date(16, 6, 2027),
    'Aug27': ql.Date(4, 8, 2027),
    'Sep27': ql.Date(29, 9, 2027),
    'Nov27': ql.Date(3, 11, 2027),
    'Dec27': ql.Date(15, 12, 2027),
    'Feb28': ql.Date(2, 2, 2028),
    'Mar28': ql.Date(22, 3, 2028),
    'May28': ql.Date(3, 5, 2028),
    'Jun28': ql.Date(21, 6, 2028),
    'Aug28': ql.Date(2, 8, 2028),
    'Sep28': ql.Date(27, 9, 2028),
    'Nov28': ql.Date(8, 11, 2028),
    'Dec28': ql.Date(13, 12, 2028),
    'Feb29': ql.Date(7, 2, 2029),
    'Mar29': ql.Date(21, 3, 2029),
    'May29': ql.Date(2, 5, 2029),
    'Jun29': ql.Date(20, 6, 2029),
    'Aug29': ql.Date(8, 8, 2029),
    'Sep29': ql.Date(26, 9, 2029),
    'Nov29': ql.Date(7, 11, 2029),
    'Dec29': ql.Date(12, 12, 2029),
    'Feb30': ql.Date(6, 2, 2030),
    'Mar30': ql.Date(20, 3, 2030),
}

def hello():
    print('hello')