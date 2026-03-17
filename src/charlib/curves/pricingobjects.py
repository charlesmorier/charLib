import numpy as np
from abc import ABC, abstractmethod
import QuantLib as ql
import charlib.utility.dates as dates


class PricingObject(ABC):
    def __init__(self, curves_bindings=None):
        self.curves_bindings = curves_bindings

    @abstractmethod
    def price(self, curves_set, rate_spread=None):
        pass

    @abstractmethod
    def implied_rate_spread(self, curves_set):
        pass


class ForwardRate(PricingObject):
    def __init__(self, start_date, end_date, curves_bindings=None):
        super().__init__(curves_bindings)
        self.start_date = dates.parse_date(start_date)
        self.end_date = dates.parse_date(end_date)

    def price(self, curves_set, rate_spread=None):
        curve = curves_set[self.curves_bindings['forecasting_curve']]
        return curve.forward_rate(self.start_date, self.end_date)

    def implied_rate_spread(self, curves_set):
        return self.price(curves_set)


class Future(PricingObject):

    def __init__(self, start_date, end_date, curves_bindings=None):
        super().__init__(curves_bindings)
        self.start_date = dates.parse_date(start_date)
        self.end_date = dates.parse_date(end_date)

    def price(self, curves_set, rate_spread=None):
        curve = curves_set[self.curves_bindings['forecasting_curve']]
        return 100.0 * (1.0 - curve.forward_rate(self.start_date, self.end_date))

    def implied_rate_spread(self, curves_set):
        return self.price(curves_set)


class Spread(PricingObject):
    def __init__(self, pricing_object1, pricing_object2):
        super().__init__()
        self.pricing_object1 = pricing_object1
        self.pricing_object2 = pricing_object2
        self.end_date = pricing_object2.end_date

        if type(pricing_object1) is not type(pricing_object2):
            raise TypeError(
                f"Type mismatch: "
                f"{type(pricing_object1).__name__} vs "
                f"{type(pricing_object2).__name__}"
            )

    def price(self, curves_set, rate_spread=None):
        return (
            self.pricing_object2.price(curves_set)
            - self.pricing_object1.price(curves_set)
        )

    def implied_rate_spread(self, curves_set):
        return (
            self.pricing_object2.implied_rate_spread(curves_set)
            - self.pricing_object1.implied_rate_spread(curves_set)
        )


class Fly(PricingObject):
    def __init__(self, pricing_object1, pricing_object2, pricing_object3):
        super().__init__()
        self.pricing_object1 = pricing_object1
        self.pricing_object2 = pricing_object2
        self.pricing_object3 = pricing_object3
        self.end_date = pricing_object3.end_date

        if not (
            type(pricing_object1) is type(pricing_object2)
            and type(pricing_object1) is type(pricing_object3)
        ):
            raise TypeError(
                f"Type mismatch: "
                f"{type(pricing_object1).__name__} vs "
                f"{type(pricing_object2).__name__} vs "
                f"{type(pricing_object3).__name__}"
            )

    def price(self, curves_set, rate_spread=None):
        return (
            2.0 * self.pricing_object2.price(curves_set)
            - self.pricing_object1.price(curves_set)
            - self.pricing_object3.price(curves_set)
        )

    def implied_rate_spread(self, curves_set):
        return (
            2.0 * self.pricing_object2.implied_rate_spread(curves_set)
            - self.pricing_object1.implied_rate_spread(curves_set)
            - self.pricing_object3.implied_rate_spread(curves_set)
        )