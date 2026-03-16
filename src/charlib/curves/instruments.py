import numpy as np
from charlib.curves import conventions
from charlib.curves import pricingobjects
from charlib.curves import swaps
from charlib.utility import dates

instruments_definitions = {

	"aud_cash_1d": {
        "start_date": "1b",
        "end_date": "1b",
        "convention": "aud.fwd.aonia",
        "ticker": "RBACOR Index"
    },

	"aud_bill_3m": {
        "start_date": "1b",
        "end_date": "3m",
        "convention": "aud.fwd.bbsw3m",
        "ticker": "BBSW3M Index"
    },

	"aud_bill_6m": {
        "start_date": "1b",
        "end_date": "6m",
        "convention": "aud.fwd.bbsw6m",
        "ticker": "BBSW6M Index"
    },

    "aud_ib_1": {
        "start_date": "bom0",
        "end_date": "eom0",
        "convention": 'aud.ib.aonia',
        "ticker": "IB1 Comdty"
    },

    "aud_ib_2": {
        "start_date": "bom1",
        "end_date": "eom1",
        "convention": "aud.ib.aonia",
        "ticker": "IB2 Comdty"
    },

    "aud_ib_3": {
        "start_date": "bom2",
        "end_date": "eom2",
        "convention": 'aud.ib.aonia',
        "ticker": "IB3 Comdty"
    },

    "aud_ib_4": {
        "start_date": "bom3",
        "end_date": "eom3",
        "convention": 'aud.ib.aonia',
        "ticker": "IB4 Comdty"
    },

    "aud_ib_5": {
        "start_date": "bom4",
        "end_date": "eom4",
        "convention": 'aud.ib.aonia',
        "ticker": "IB5 Comdty"
    },

    "aud_ib_6": {
        "start_date": "bom5",
        "end_date": "eom5",
        "convention": 'aud.ib.aonia',
        "ticker": "IB6 Comdty"
    },

    "aud_ib_7": {
        "start_date": "bom6",
        "end_date": "eom6",
        "convention": 'aud.ib.aonia',
        "ticker": "IB7 Comdty"
    },

    "aud_ib_8": {
        "start_date": "bom7",
        "end_date": "eom7",
        "convention": 'aud.ib.aonia',
        "ticker": "IB8 Comdty"
    },

    "aud_ib_9": {
        "start_date": "bom8",
        "end_date": "eom8",
        "convention": 'aud.ib.aonia',
        "ticker": "IB9 Comdty"
    },

    "aud_ib_10": {
        "start_date": "bom9",
        "end_date": "eom9",
        "convention": 'aud.ib.aonia',
        "ticker": "IB10 Comdty"
    },

    "aud_ib_11": {
        "start_date": "bom10",
        "end_date": "eom10",
        "convention": 'aud.ib.aonia',
        "ticker": "IB11 Comdty"
    },

    "aud_ib_12": {
        "start_date": "bom11",
        "end_date": "eom11",
        "convention": 'aud.ib.aonia',
        "ticker": "IB12 Comdty"
    },

	"aud_ois_rba1": {
        "start_date": "rba1",
        "end_date": "rba2",
        "convention": "aud.fwd.aonia",
        "ticker": "ADSF1A IAUS Comdty"
    },

	"aud_ois_rba2": {
        "start_date": "rba2",
        "end_date": "rba3",
        "convention": "aud.fwd.aonia",
        "ticker": "ADSF2A IAUS Curncy"
    },

	"aud_ois_rba3": {
        "start_date": "rba3",
        "end_date": "rba4",
        "convention": "aud.fwd.aonia",
        "ticker": "ADSF3 IAUS Curncy"
    },

	"aud_ois_rba4": {
        "start_date": "rba4",
        "end_date": "rba5",
        "convention": "aud.fwd.aonia",
        "ticker": "ADSF4A IAUS Curncy"
    },

	"aud_ois_rba5": {
        "start_date": "rba5",
        "end_date": "rba6",
        "convention": "aud.fwd.aonia",
        "ticker": "ADSF5A IAUS Curncy"
    },

	"aud_ois_rba6": {
        "start_date": "rba6",
        "end_date": "rba7",
        "convention": "aud.fwd.aonia",
        "ticker": "ADSF6A IAUS Curncy"
    },

	"aud_ois_rba7": {
        "start_date": "rba7",
        "end_date": "rba8",
        "convention": "aud.fwd.aonia",
        "ticker": "ADSF7A IAUS Curncy"
    },

	"aud_ois_rba8": {
        "start_date": "rba8",
        "end_date": "rba9",
        "convention": "aud.fwd.aonia",
        "ticker": "ADSF8A IAUS Curncy"
    },

	"aud_ois_rba9": {
        "start_date": "rba9",
        "end_date": "rba10",
        "convention": "aud.fwd.aonia",
        "ticker": "ADSF9A IAUS Curncy"
    },

	"aud_ois_rba10": {
        "start_date": "rba10",
        "end_date": "rba11",
        "convention": "aud.fwd.aonia",
        "ticker": "ADSF10A IAUS Curncy"
    },

	"aud_ois_rba11": {
        "start_date": "rba11",
        "end_date": "rba12",
        "convention": "aud.fwd.aonia",
        "ticker": "ADSF11A IAUS Curncy"
    },

	"aud_ois_rba12": {
        "start_date": "rba12",
        "end_date": "rba13",
        "convention": "aud.fwd.aonia",
        "ticker": "ADSF12A IAUS Curncy"
    },

	"aud_sfe_1": {
        "start_date": "sfe1",
        "end_date": "3m",
        "convention": "aud.sfe.bbsw3m",
        "ticker": "IR1 Comdty"
    },

	"aud_sfe_2": {
        "start_date": "sfe2",
        "end_date": "3m",
        "convention": "aud.sfe.bbsw3m",
        "ticker": "IR2 Comdty"
    },

	"aud_sfe_3":{
        "start_date": "sfe3",
        "end_date": "3m",
        "convention": "aud.sfe.bbsw3m",
        "ticker": "IR3 Comdty"
    },

	"aud_sfe_4": {
        "start_date": "sfe4",
        "end_date": "3m",
        "convention": "aud.sfe.bbsw3m",
        "ticker": "IR4 Comdty"
    },

	"aud_sfe_5": {
        "start_date": "sfe5",
        "end_date": "3m",
        "convention": "aud.sfe.bbsw3m",
        "ticker": "IR5 Comdty"
    },

	"aud_sfe_6": {
        "start_date": "sfe6",
        "end_date": "3m",
        "convention": "aud.sfe.bbsw3m",
        "ticker": "IR6 Comdty"
    },

	"aud_sfe_7": {
        "start_date": "sfe7",
        "end_date": "3m",
        "convention": "aud.sfe.bbsw3m",
        "ticker": "IR7 Comdty"
    },

	"aud_sfe_8": {
        "start_date": "sfe8",
        "end_date": "3m",
        "convention": "aud.sfe.bbsw3m",
        "ticker": "IR8 Comdty"
    },

	"aud_sfe_9": {
        "start_date": "sfe9",
        "end_date": "3m",
        "convention": "aud.sfe.bbsw3m",
        "ticker": "IR9 Comdty"},

	"aud_irs_3y": {
        "start_date": "1b",
        "end_date": "3y",
        "convention": "aud.irs.qq.bbsw.aonia",
        "ticker": "ADSWAP3Q Comdty"
    },

	"aud_irs_4y": {
        "start_date": "1b",
        "end_date": "4y",
        "convention": "aud.irs.ss.bbsw.aonia",
        "ticker": "ADSWAP4 Comdty"
    },

	"aud_irs_5y": {
        "start_date": "1b",
        "end_date": "3y",
        "convention": "aud.irs.ss.bbsw.aonia",
        "ticker": "ADSWAP5 Comdty"
    },

	"aud_irs_6y": {
        "start_date": "1b",
        "end_date": "6y",
        "convention": "aud.irs.ss.bbsw.aonia",
        "ticker": "ADSWAP6 Comdty"
    },

	"aud_irs_7y": {
        "start_date": "1b",
        "end_date": "7y",
        "convention": "aud.irs.ss.bbsw.aonia",
        "ticker": "ADSWAP7 Comdty"
    },

	"aud_irs_8y": {
        "start_date": "1b",
        "end_date": "8y",
        "convention": "aud.irs.ss.bbsw.aonia",
        "ticker": "ADSWAP8 Comdty"
    },

	"aud_irs_9y": {
        "start_date": "1b",
        "end_date": "9y",
        "convention": "aud.irs.ss.bbsw.aonia",
        "ticker": "ADSWAP9 Comdty"
    },

	"aud_irs_10y": {
        "start_date": "1b",
        "end_date": "10y",
        "convention": "aud.irs.ss.bbsw.aonia",
        "ticker": "ADSWAP10 Comdty"
    },

	"aud_irs_12y": {
        "start_date": "1b",
        "end_date": "12y",
        "convention": "aud.irs.ss.bbsw.aonia",
        "ticker": "ADSWAP12 Comdty"
    },

	"aud_irs_15y": {
        "start_date": "1b",
        "end_date": "15y",
        "convention": "aud.irs.ss.bbsw.aonia",
        "ticker": "ADSWAP15 Comdty"
    },

	"aud_irs_20y": {
        "start_date": "1b",
        "end_date": "20y",
        "convention": "aud.irs.ss.bbsw.aonia",
        "ticker": "ADSWAP20 Comdty"
    },

	"aud_irs_25y": {
        "start_date": "1b",
        "end_date": "25y",
        "convention": "aud.irs.ss.bbsw.aonia",
        "ticker": "ADSWAP25 Comdty"
    },

	"aud_irs_30y": {
        "start_date": "1b",
        "end_date": "30y",
        "convention": "aud.irs.ss.bbsw.aonia",
        "ticker": "ADSWAP30 Comdty"
    },


	"aud_bob_sfe1": {
        "start_date": "sfe1",
        "end_date": "3m",
        "convention": "aud.tbs.qq.aonia.bbsw.aonia",
        "ticker": "ADFSPS1 IAUS Comdty"},

	"aud_bob_sfe2": {
        "start_date": "sfe2",
        "end_date": "3m",
        "convention": "aud.tbs.qq.aonia.bbsw.aonia",
        "ticker": "ADFSPS2 IAUS Comdty"},

	"aud_bob_sfe3": {
        "start_date": "sfe3",
        "end_date": "3m",
        "convention": "aud.tbs.qq.aonia.bbsw.aonia",
        "ticker": "ADFSPS3 IAUS Comdty"},

	"aud_bob_sfe4": {
        "start_date": "sfe4",
        "end_date": "3m",
        "convention": "aud.tbs.qq.aonia.bbsw.aonia",
        "ticker": "ADFSPS4 IAUS Comdty"},

	"aud_bob_sfe5": {
        "start_date": "sfe5",
        "end_date": "3m",
        "convention": "aud.tbs.qq.aonia.bbsw.aonia",
        "ticker": "ADFSPS5 IAUS Comdty"},

	"aud_bob_sfe6": {
        "start_date": "sfe6",
        "end_date": "3m",
        "convention": "aud.tbs.qq.aonia.bbsw.aonia",
        "ticker": "ADFSPS6 IAUS Comdty"},

	"aud_bob_sfe7": {
        "start_date": "sfe7",
        "end_date": "3m",
        "convention": "aud.tbs.qq.aonia.bbsw.aonia",
        "ticker": "ADFSPS7 IAUS Comdty"},

	"aud_bob_sfe8": {
        "start_date": "sfe8",
        "end_date": "3m",
        "convention": "aud.tbs.qq.aonia.bbsw.aonia",
        "ticker": "ADFSPS8 IAUS Comdty"},

	"aud_bob_sfe9": {
        "start_date": "sfe9",
        "end_date": "3m",
        "convention": "aud.tbs.qq.aonia.bbsw.aonia",
        "ticker": "ADFSPS9 IAUS Comdty"},

	"aud_bob_1y": {
        "start_date": "1b",
        "end_date": "1y",
        "convention": "aud.tbs.qq.aonia.bbsw.aonia",
        "ticker": "ADOIQQ1 IAUS Comdty"},

	"aud_bob_18m": {
        "start_date": "1b",
        "end_date": "18m",
        "convention": "aud.tbs.qq.aonia.bbsw.aonia",
        "ticker": "ADOIQQ1F Comdty"
    },

	"aud_bob_2y": {
        "start_date": "1b",
        "end_date": "2y",
        "convention": "aud.tbs.qq.aonia.bbsw.aonia",
        "ticker": "ADOIQQ2 Comdty"
    },

	"aud_bob_3y": {
        "start_date": "1b",
        "end_date": "3y",
        "convention": "aud.tbs.qq.aonia.bbsw.aonia",
        "ticker": "ADOIQQ3 Comdty"
    },

	"aud_bob_4y": {
        "start_date": "1b",
        "end_date": "4y",
        "convention": "aud.tbs.qq.aonia.bbsw.aonia",
        "ticker": "ADOIQQ4 Comdty"
    },

	"aud_bob_5y": {
        "start_date": "1b",
        "end_date": "5y",
        "convention": "aud.tbs.qq.aonia.bbsw.aonia",
        "ticker": "ADOIQQ5 Comdty"
    },

	"aud_bob_6y": {
        "start_date": "1b",
        "end_date": "6y",
        "convention": "aud.tbs.qq.aonia.bbsw.aonia",
        "ticker": "ADOIQQ6 Comdty"
    },

	"aud_bob_7y": {
        "start_date": "1b",
        "end_date": "7y",
        "convention": "aud.tbs.qq.aonia.bbsw.aonia",
        "ticker": "ADOIQQ7 Comdty"
    },

	"aud_bob_8y": {
        "start_date": "1b",
        "end_date": "8y",
        "convention": "aud.tbs.qq.aonia.bbsw.aonia",
        "ticker": "ADOIQQ8 Comdty"
    },

	"aud_bob_9y": {
        "start_date": "1b",
        "end_date": "9y",
        "convention": "aud.tbs.qq.aonia.bbsw.aonia",
        "ticker": "ADOIQQ9 Comdty"
    },

	"aud_bob_10y": {
        "start_date": "1b",
        "end_date": "10y",
        "convention": "aud.tbs.qq.aonia.bbsw.aonia",
        "ticker": "ADOIQQ10 Comdty"
    },

	"aud_bob_12y": {
        "start_date": "1b",
        "end_date": "12y",
        "convention": "aud.tbs.qq.aonia.bbsw.aonia",
        "ticker": "ADOIQQ12 Comdty"
    },

	"aud_bob_15y": {
        "start_date": "1b",
        "end_date": "15y",
        "convention": "aud.tbs.qq.aonia.bbsw.aonia",
        "ticker": "ADOIQQ15 Comdty"
    },

	"aud_bob_20y": {
        "start_date": "1b",
        "end_date": "20y",
        "convention": "aud.tbs.qq.aonia.bbsw.aonia",
        "ticker": "ADOIQQ20 Comdty"
    },

	"aud_bob_30y": {
        "start_date": "1b",
        "end_date": "30y",
        "convention": "aud.tbs.qq.aonia.bbsw.aonia",
        "ticker": "ADOIQQ30 Comdty"
    },

	"aud_6s3s_6m": {
        "start_date": "1b",
        "end_date": "6m",
        "convention": "aud.tbs.qs.bbsw.bbsw.aonia",
        "ticker": "ADBBCFF Comdty"
    },

	"aud_6s3s_1y": {
        "start_date": "1b",
        "end_date": "1y",
        "convention": "aud.tbs.qs.bbsw.bbsw.aonia",
        "ticker": "ADBBCF1 Comdty"
    },

	"aud_6s3s_18m": {
        "start_date": "1b",
        "end_date": "18m",
        "convention": "aud.tbs.qs.bbsw.bbsw.aonia",
        "ticker": "ADBBCF1F Comdty"
    },

	"aud_6s3s_2y": {
        "start_date": "1b",
        "end_date": "2y",
        "convention": "aud.tbs.qs.bbsw.bbsw.aonia",
        "ticker": "ADBBCF2 Comdty"
    },

	"aud_6s3s_3y": {
        "start_date": "1b",
        "end_date": "3y",
        "convention": "aud.tbs.qs.bbsw.bbsw.aonia",
        "ticker": "ADBBCF3 Comdty"
    },

	"aud_6s3s_4y": {
        "start_date": "1b",
        "end_date": "4y",
        "convention": "aud.tbs.qs.bbsw.bbsw.aonia",
        "ticker": "ADBBCF4 Comdty"
    },

	"aud_6s3s_5y": {
        "start_date": "1b",
        "end_date": "5y",
        "convention": "aud.tbs.qs.bbsw.bbsw.aonia",
        "ticker": "ADBBCF5 Comdty"
    },

	"aud_6s3s_6y": {
        "start_date": "1b",
        "end_date": "6y",
        "convention": "aud.tbs.qs.bbsw.bbsw.aonia",
        "ticker": "ADBBCF6 Comdty"
    },

	"aud_6s3s_7y": {
        "start_date": "1b",
        "end_date": "7y",
        "convention": "aud.tbs.qs.bbsw.bbsw.aonia",
        "ticker": "ADBBCF7 Comdty"
    },

	"aud_6s3s_8y": {
        "start_date": "1b",
        "end_date": "8y",
        "convention": "aud.tbs.qs.bbsw.bbsw.aonia",
        "ticker": "ADBBCF8 Comdty"
    },

	"aud_6s3s_9y": {
        "start_date": "1b",
        "end_date": "9y",
        "convention": "aud.tbs.qs.bbsw.bbsw.aonia",
        "ticker": "ADBBCF9 Comdty"
    },

	"aud_6s3s_10y": {
        "start_date": "1b",
        "end_date": "10y",
        "convention": "aud.tbs.qs.bbsw.bbsw.aonia",
        "ticker": "ADBBCF10 Comdty"
    },

	"aud_6s3s_12y": {
        "start_date": "1b",
        "end_date": "12y",
        "convention": "aud.tbs.qs.bbsw.bbsw.aonia",
        "ticker": "ADBBCF12 Comdty"
    },

	"aud_6s3s_15y": {
        "start_date": "1b",
        "end_date": "15y",
        "convention": "aud.tbs.qs.bbsw.bbsw.aonia",
        "ticker": "ADBBCF15 Comdty"
    },

	"aud_6s3s_20y": {
        "start_date": "1b",
        "end_date": "20y",
        "convention": "aud.tbs.qs.bbsw.bbsw.aonia",
        "ticker": "ADBBCF20 Comdty"
    },

	"aud_6s3s_25y": {
        "start_date": "1b",
        "end_date": "25y",
        "convention": "aud.tbs.qs.bbsw.bbsw.aonia",
        "ticker": "ADBBCF25 Comdty"
    },

	"aud_6s3s_30y": {
        "start_date": "1b",
        "end_date": "30y",
        "convention": "aud.tbs.qs.bbsw.bbsw.aonia",
        "ticker": "ADBBCF30 Comdty"
    },
}


def create_pricing_object_from_convention(start_date, end_date, notional, convention):
    this_start_date = dates.parse_date(start_date)
    this_end_date = dates.parse_date(end_date, this_start_date)
    this_convention = conventions.all_conventions[convention]

    if this_convention['type'] in (swaps.VanillaSwap, swaps.TermBasisSwap):
        return create_swap_from_convention(this_start_date, end_date, notional, convention)
    else:
        return this_convention['type'](this_start_date, this_end_date, this_convention['curves_bindings'])
        #return pricingobjects.ForwardRate(
        #    this_start_date,
        #    this_end_date,
        #    this_convention['curves_bindings'],
        #)


def create_swap_from_convention(start_date, end_date, notional, convention):
    this_start_date = dates.parse_date(start_date)
    this_end_date = dates.parse_date(end_date, this_start_date)
    this_convention = conventions.all_conventions[convention]

    return this_convention['type'](
        this_start_date,
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


def run_test():
    bill = create_pricing_object_from_convention('1b', '3m', 1, 'aud.fwd.bbsw3m')
    print(bill.start_date)
    print(bill.end_date)
    rba = create_pricing_object_from_convention("rba1", "rba2", 1, 'aud.fwd.aonia')
    print(rba.start_date)
    print(rba.end_date)
    swap = create_swap_from_convention("1b", "3y", 1, "aud.irs.qq.bbsw.aonia")
    print(swap.start_date)
    print(swap.end_date)




#run_test()