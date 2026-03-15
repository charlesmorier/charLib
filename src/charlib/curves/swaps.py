import numpy as np
from abc import ABC, abstractmethod
import QuantLib as ql
from charlib.curves import pricingobjects


class SwapLeg(pricingobjects.PricingObject):
    def __init__(
        self,
        start_date,
        end_date,
        leg_details,
        rule=ql.DateGeneration.Forward,
        eom=False,
        curves_bindings=None
    ):
        super().__init__(curves_bindings)

        self.leg_details = leg_details

        self._ql_accrual_schedule = ql.Schedule(start_date, end_date,
                                               leg_details['frequency'],
                                               leg_details['payment_calendar'],
                                               leg_details['accrual_business_days_convention'],
                                               leg_details['accrual_business_days_convention'],
                                               rule, eom)

        self.accrual_schedule = list(self._ql_accrual_schedule)

        self.accrual_yfs = [
            leg_details['daycount_convention'].yearFraction(t0, t1)
            for t0, t1 in zip(self.accrual_schedule, self.accrual_schedule[1:])
        ]

        self._ql_payment_schedule = ql.Schedule(start_date, end_date,
                                                leg_details['frequency'],
                                                leg_details['payment_calendar'],
                                                leg_details['payment_business_days_convention'],
                                                leg_details['payment_business_days_convention'],
                                                rule, eom)

        self.payment_schedule = list(self._ql_payment_schedule)[1:]

        if leg_details['payment_lag'] is not None:
            self.payment_schedule = [
                leg_details['payment_calendar'].advance(
                    t, leg_details['payment_lag'], leg_details['payment_business_days_convention']
                )
                for t in self.payment_schedule
            ]

        self.fwd_rates = []
        self.discount_factors = []

    @abstractmethod
    def price(self, curves_set, rate_spread=None):
        pass

    @property
    def end_date(self):
        return self.payment_schedule[-1]

    @abstractmethod
    def implied_rate_spread(self, curves_set, rate_spread=None):
        pass


class FixedSwapLeg(SwapLeg):
    def __init__(
        self,
        start_date,
        end_date,
        leg_details,
        rule=ql.DateGeneration.Forward,
        eom=False,
        curves_bindings=None,
    ):
        super().__init__(start_date, end_date, leg_details, rule, eom, curves_bindings)

    def price(self, curves_set, rate_spread=1):
        df = curves_set[self.curves_bindings['discounting_curve']].discount_factor(
            self.payment_schedule
        )
        self.discount_factors = df

        cash_flows = np.array(self.accrual_yfs) * rate_spread * np.array(df)
        return float(np.sum(cash_flows))

    def implied_rate_spread(self, curves_set, rate_spread=None):
        raise RuntimeError("Not implemented for this class")


class FloatingSwapLeg(SwapLeg):
    def __init__(
        self,
        start_date,
        end_date,
        leg_details,
        rule=ql.DateGeneration.Forward,
        eom=False,
        curves_bindings=None,
    ):
        super().__init__(start_date, end_date, leg_details, rule, eom, curves_bindings)

        if leg_details['frequency'] == ql.Period(ql.NoFrequency):
            self.fixing_schedule = [self.accrual_schedule[-1]]
        else:
            self.fixing_schedule = [
                leg_details['fixing_calendar'].advance(t, leg_details['frequency'], ql.Following)
                for t in self.accrual_schedule[:-1]
            ]

    def price(self, curves_set, rate_spread=0):
        fwd_curve = curves_set[self.curves_bindings['forecasting_curve']]
        disc_curve = curves_set[self.curves_bindings['discounting_curve']]

        self.fwd_rates = fwd_curve.forward_rate(
            self.accrual_schedule[:-1],
            self.fixing_schedule
        )
        self.discount_factors = disc_curve.discount_factor(self.payment_schedule)

        cash_flows = (
            np.array(self.accrual_yfs)
            * (np.array(self.fwd_rates) + rate_spread)
            * np.array(self.discount_factors)
        )

        return float(np.sum(cash_flows))

    def implied_rate_spread(self, curves_set, rate_spread=None):
        raise RuntimeError("Not implemented for this class")


class Swap(pricingobjects.PricingObject):
    def __init__(
        self,
        start_date,
        end_date,
        currency,
        notional,
        left_leg_details,
        right_leg_details,
        curves_bindings=None,
    ):
        super().__init__(curves_bindings)
        if isinstance(start_date, ql.Date):
            self.start_date = start_date
        else:
            self.start_date = start_date

        if isinstance(end_date, ql.Date):
            self.end_date_unadj = end_date
        else:
            self.end_date_unadj = left_leg_details['payment_calendar'].advance(
                start_date, ql.Period(end_date), ql.Unadjusted
            )

        self.end_date = self.end_date_unadj
        self.currency = currency
        self.notional = notional
        self.left_leg_details = left_leg_details
        self.right_leg_details = right_leg_details

    @abstractmethod
    def price(self, curves_set, rate_spread=None):
        pass

    @abstractmethod
    def implied_rate_spread(self, curves_set, rate_spread=None):
        pass


class VanillaSwap(Swap):
    def __init__(
        self,
        start_date,
        end_date,
        currency,
        notional,
        left_leg_details,
        right_leg_details,
        curves_bindings,
    ):
        super().__init__(
            start_date, end_date, currency, notional, left_leg_details, right_leg_details, curves_bindings
        )

        self.left_swap_leg = FixedSwapLeg(start_date, self.end_date_unadj, left_leg_details)
        self.left_swap_leg.curves_bindings = {
            'discounting_curve': self.curves_bindings['discounting_curve']
        }

        self.right_swap_leg = FloatingSwapLeg(start_date, self.end_date_unadj, right_leg_details)
        self.right_swap_leg.curves_bindings = {
            'discounting_curve': self.curves_bindings['discounting_curve'],
            'forecasting_curve': self.curves_bindings['forecasting_curve'],
        }

        self.end_date = self.left_swap_leg.end_date

    def price(self, curves_set, rate_spread=1):
        left_leg_npv = self.left_swap_leg.price(curves_set, rate_spread)
        right_leg_npv = self.right_swap_leg.price(curves_set)
        return self.notional * (left_leg_npv - right_leg_npv)

    def implied_rate_spread(self, curves_set):
        left_leg_npv = self.left_swap_leg.price(curves_set, 1)
        right_leg_npv = self.right_swap_leg.price(curves_set)
        #print(left_leg_npv)
        #print(right_leg_npv)
        return right_leg_npv / left_leg_npv


class TermBasisSwap(Swap):
    def __init__(
        self,
        start_date,
        end_date,
        currency,
        notional,
        left_leg_details,
        right_leg_details,
        curves_bindings,
    ):
        super().__init__(
            start_date, end_date, currency, notional, left_leg_details, right_leg_details, curves_bindings
        )

        self.left_swap_leg = FloatingSwapLeg(start_date, self.end_date_unadj, left_leg_details)
        self.left_swap_leg.curves_bindings = {
            'discounting_curve': self.curves_bindings['discounting_curve'],
            'forecasting_curve': self.curves_bindings['left_leg_forecasting_curve'],
        }

        self.right_swap_leg = FloatingSwapLeg(start_date, self.end_date_unadj, right_leg_details)
        self.right_swap_leg.curves_bindings = {
            'discounting_curve': self.curves_bindings['discounting_curve'],
            'forecasting_curve': self.curves_bindings['right_leg_forecasting_curve'],
        }

        self.end_date = self.left_swap_leg.end_date

    def price(self, curves_set, rate_spread=0):
        left_leg_npv = self.left_swap_leg.price(curves_set, rate_spread)
        right_leg_npv = self.right_swap_leg.price(curves_set)
        return self.notional * (left_leg_npv - right_leg_npv)

    def implied_rate_spread(self, curves_set, rate_spread=None):
        left_leg_npv = self.left_swap_leg.price(curves_set, 0)
        right_leg_npv = self.right_swap_leg.price(curves_set, 0)

        annuity_leg = FixedSwapLeg(self.start_date, self.end_date_unadj, self.left_leg_details)
        annuity_leg.curves_bindings = self.left_swap_leg.curves_bindings
        annuity_npv = annuity_leg.price(curves_set)

        return (right_leg_npv - left_leg_npv) / annuity_npv