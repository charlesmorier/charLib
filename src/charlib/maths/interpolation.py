import numpy as np
from scipy.interpolate import (
    interp1d, CubicSpline, make_interp_spline,
    PchipInterpolator, Akima1DInterpolator
)
import QuantLib as ql


class InterpolationEngine:
    def __init__(self, x, y, scheme="linear", split_interpolation=None):
        if not np.all(np.diff(x) > 0):
            raise ValueError("Array x must be in ascending order")

        self.x = x
        self.y = y
        self.scheme = scheme
        self.split_interpolation = split_interpolation

        if self.split_interpolation is not None:
            if not isinstance(self.split_interpolation, dict):
                raise TypeError(
                    f"split_interpolation must be a dict; got {type(self.split_interpolation).__name__}"
                )

            self.is_split = True
            self.split_scheme = self.split_interpolation["scheme"]
            self.split_node = self.split_interpolation["node"]

            if isinstance(self.split_node, ql.Date):
                self._split_x = ql.Actual365Fixed().yearFraction(
                    ql.Date.todaysDate(), self.split_node
                )
            else:
                self._split_x = self.split_node

            self._split_at = np.where(np.isclose(self.x, self._split_x))[0][0]

            self._x_L = self.x[: self._split_at + 1]
            self._x_R = self.x[self._split_at :]

        else:
            self.is_split = False

        # Build interpolation on init
        self._build_interpolators()

    @property
    def y(self):
        return self._y

    @y.setter
    def y(self, y):
        self._y = y
        self._build_interpolators()

    def _build_interpolators(self):
        if self._y is None:
            return

        if self.is_split:
            self._y_L = self._y[: self._split_at + 1]
            self._y_R = self._y[self._split_at :]

            self._interp_L = self._set_scheme(self._x_L, self._y_L, self.scheme)
            self._interp_R = self._set_scheme(self._x_R, self._y_R, self.split_scheme)
        else:
            self._interp_L = self._set_scheme(self.x, self._y, self.scheme)
            self._interp_R = None

    def _set_scheme(self, x, y, scheme):
        if scheme == "linear":
            return interp1d(
                x, y, kind="linear", bounds_error=False,
                fill_value=(y[0], y[-1])
            )

        if scheme == "cubic":
            return CubicSpline(x, y, extrapolate=True)

        if scheme == "bspline":
            return make_interp_spline(x, y, k=3)

        if scheme == "pchip":
            return PchipInterpolator(x, y, extrapolate=True)

        if scheme == "akima":
            return Akima1DInterpolator(x, y)

        raise ValueError(f"Unknown interpolation scheme: {scheme}")

    def interpolate(self, x_star):
        if not self.is_split:
            return self._interp_L(x_star)

        if isinstance(x_star, float):
            return (
                self._interp_L(x_star)
                if x_star <= self._split_x
                else self._interp_R(x_star)
            )

        x_star = np.asarray(x_star)

        mask_L = x_star <= self._split_x
        mask_R = ~mask_L

        y = np.empty_like(x_star, dtype=float)
        y[mask_L] = self._interp_L(x_star[mask_L])
        y[mask_R] = self._interp_R(x_star[mask_R])

        return y 