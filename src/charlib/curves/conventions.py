import QuantLib as ql
from charlib.curves import swaps, pricingobjects
 
 
### To be completed over time
 
# Calendars
calendar_australia = ql.Australia()
 
# Conventions
convention_following = ql.Following
convention_modified_following = ql.ModifiedFollowing
 
# Periods
period_2b = ql.Period(2, ql.Days)
period_zero = ql.Period(ql.NoFrequency)
period_quarterly = ql.Period(3, ql.Months)
period_semiannual = ql.Period(6, ql.Months)
period_annual = ql.Period(1, ql.Years)
 
# Daycount Conventions
daycount_act365_fixed = ql.Actual365Fixed()
 
 
 
all_conventions = {
 
    'aud.fwd.aonia': {
        'type': pricingobjects.ForwardRate,
        'ccy': 'aud',
        'calendar': calendar_australia,
        'curves_bindings': {'forecasting_curve': 'aud.aonia.1d'},
        'scale': 100
    },
 
    'aud.fwd.bbsw3m': {
        'type': pricingobjects.ForwardRate,
        'ccy': 'aud',
        'calendar': calendar_australia,
        'curves_bindings': {'forecasting_curve': 'aud.bbsw.3m'},
        'scale': 100
    },
 
    'aud.fwd.bbsw6m': {
        'type': pricingobjects.ForwardRate,
        'ccy': 'aud',
        'calendar': calendar_australia,
        'curves_bindings': {'forecasting_curve': 'aud.bbsw.6m'},
        'scale': 100
    },
 
    'aud.irs.zz.aonia.aonia': {
        'type': swaps.VanillaSwap,
        'ccy': 'aud',
        'left_leg': {'frequency': period_zero,
        'daycount_convention': daycount_act365_fixed,
        'payment_calendar': calendar_australia,
        'accrual_business_days_convention': convention_modified_following,
        'payment_business_days_convention': convention_following,
        'payment_lag': None},
        'right_leg': {'frequency': period_zero,
                      'daycount_convention': daycount_act365_fixed,
                      'fixing_calendar': calendar_australia,
                      'payment_calendar': calendar_australia,
                      'accrual_business_days_convention': convention_modified_following,
                      'payment_business_days_convention': convention_following,
                      'payment_lag': None},
        'curves_bindings': {'discounting_curve': 'aud.aonia.1', 'forecasting_curve': 'aud.aonia.1d'},
        'scale': 100
    },
 
    'aud.irs.aa.aonia.aonia': {
        'type': swaps.VanillaSwap,
        'ccy': 'aud',
        'left_leg': {'frequency': period_annual,
                     'daycount_convention': daycount_act365_fixed,
                     'payment_calendar': calendar_australia,
                     'accrual_business_days_convention': convention_modified_following,
                     'payment_business_days_convention': convention_following,
                     'payment_lag': period_2b},
        'right_leg': {'frequency': period_annual,
                      'daycount_convention': daycount_act365_fixed,
                      'fixing_calendar': calendar_australia,
                      'payment_calendar': calendar_australia,
                      'accrual_business_days_convention': convention_modified_following,
                      'payment_business_days_convention': convention_following,
                      'payment_lag': period_2b},
        'curves_bindings': {'discounting_curve': 'aud.aonia.1d', 'forecasting_curve': 'aud.aonia.1d'},
        'scale': 100
    },
 
    'aud.irs.qq.aonia.aonia': {
        'type': swaps.VanillaSwap,
        'ccy': 'aud',
        'left_leg': {'frequency': period_quarterly,
                     'daycount_convention': daycount_act365_fixed,
                     'payment_calendar': calendar_australia,
                     'accrual_business_days_convention': convention_modified_following,
                     'payment_business_days_convention': convention_following,
                     'payment_lag': None},
        'right_leg': {'frequency': period_quarterly,
                      'daycount_convention': daycount_act365_fixed,
                      'fixing_calendar': calendar_australia,
                      'payment_calendar': calendar_australia,
                      'accrual_business_days_convention': convention_modified_following,
                      'payment_business_days_convention': convention_following,
                      'payment_lag': None},
        'curves_bindings': {'discounting_curve': 'aud.aonia.1d', 'forecasting_curve': 'aud.aonia.1d'},
        'scale': 100
    },
 
    'aud.irs.qq.bbsw.aonia': {
        'type': swaps.VanillaSwap,
        'ccy': 'aud',
        'left_leg': {'frequency': period_quarterly,
                     'daycount_convention': daycount_act365_fixed,
                     'payment_calendar': calendar_australia,
                     'accrual_business_days_convention': convention_modified_following,
                     'payment_business_days_convention': convention_following,
                     'payment_lag': None},
        'right_leg': {'frequency': period_quarterly,
                      'daycount_convention': daycount_act365_fixed,
                      'fixing_calendar': calendar_australia,
                      'payment_calendar': calendar_australia,
                      'accrual_business_days_convention': convention_modified_following,
                      'payment_business_days_convention': convention_following,
                      'payment_lag': None},
        'curves_bindings': {'discounting_curve': 'aud.aonia.1d', 'forecasting_curve': 'aud.bbsw.3m'},
        'scale': 100
    },
    
    'aud.irs.ss.bbsw.aonia': {
        'type': swaps.VanillaSwap,
        'ccy': 'aud',
        'left_leg': {'frequency': period_semiannual,
                     'daycount_convention': daycount_act365_fixed,
                     'payment_calendar': calendar_australia,
                     'accrual_business_days_convention': convention_modified_following,
                     'payment_business_days_convention': convention_following,
                     'payment_lag': None},
        'right_leg': {'frequency': period_semiannual,
                      'daycount_convention': daycount_act365_fixed,
                      'fixing_calendar': calendar_australia,
                      'payment_calendar': calendar_australia,
                      'accrual_business_days_convention': convention_modified_following,
                      'payment_business_days_convention': convention_following,
                      'payment_lag': None},
        'curves_bindings': {'discounting_curve': 'aud.aonia.1d', 'forecasting_curve': 'aud.bbsw.6m'},
        'scale': 100
    },
    
    'aud.tbs.qq.aonia.bbsw.aonia': {
        'type': swaps.TermBasisSwap,
        'ccy': 'aud',
        'left_leg': {'frequency': period_quarterly,
                     'daycount_convention': daycount_act365_fixed,
                     'fixing_calendar': calendar_australia,
                     'payment_calendar': calendar_australia,
                     'accrual_business_days_convention': convention_modified_following,
                     'payment_business_days_convention': convention_following,
                     'payment_lag': None},
        'right_leg': {'frequency': period_quarterly,
                      'daycount_convention': daycount_act365_fixed,
                      'fixing_calendar': calendar_australia,
                      'payment_calendar': calendar_australia,
                      'accrual_business_days_convention': convention_modified_following,
                      'payment_business_days_convention': convention_following,
                      'payment_lag': None},
        'curves_bindings': {'discounting_curve': 'aud.aonia.1d', 'left_leg_forecasting_curve': 'aud.aonia.1d', 'right_leg_forecasting_curve': 'aud.bbsw.3m'},
        'scale': 10000
    },
    
    'aud.tbs.qs.bbsw.bbsw.aonia': {
        'type': swaps.TermBasisSwap,
        'ccy': 'aud',
        'left_leg': {'frequency': period_quarterly,
                     'daycount_convention': daycount_act365_fixed,
                     'fixing_calendar': calendar_australia,
                     'payment_calendar': calendar_australia,
                     'accrual_business_days_convention': convention_modified_following,
                     'payment_business_days_convention': convention_following,
                     'payment_lag': None},
        'right_leg': {'frequency': period_semiannual,
                      'daycount_convention': daycount_act365_fixed,
                      'fixing_calendar': calendar_australia,
                      'payment_calendar': calendar_australia,
                      'accrual_business_days_convention': convention_modified_following,
                      'payment_business_days_convention': convention_following,
                      'payment_lag': None},
        'curves_bindings': {'discounting_curve': 'aud.aonia.1d', 'left_leg_forecasting_curve': 'aud.bbsw.3m', 'right_leg_forecasting_curve': 'aud.bbsw.6m'},
        'scale': 10000
    },
}