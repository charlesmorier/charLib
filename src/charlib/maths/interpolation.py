import numpy as np
from scipy.interpolate import (
    interp1d, CubicSpline, make_interp_spline,
    PchipInterpolator, Akima1DInterpolator
)
import QuantLib as ql



INTERPOLATION_SCHEMES_MAP = frozenset({'linear', 'cubic', 'bspline', 'pchip', 'akima'})
_Interpolator = interp1d | CubicSpline | PchipInterpolator | Akima1DInterpolator


class InterpolationEngine:

    def __init__(self, x, y, scheme: str = "linear", split_scheme: str | None = None, split_node: float | ql.Date | None = None):
        x = np.asarray(x, dtype=float)
        if x.ndim != 1:
            raise ValueError("x must be in 1d.")
        if not np.all(np.diff(x) > 0):
            raise ValueError("x must be strictly increasing.")
        if scheme not in INTERPOLATION_SCHEMES_MAP:
            raise ValueError(f"Unknown interpolation scheme: {scheme}")
        if (split_scheme is None) != (split_node is None):
            raise ValueError("split_scheme and split_node must both be provided, or neither.")
        if split_scheme is not None and split_scheme not in INTERPOLATION_SCHEMES_MAP:
            raise ValueError(f"Unknown split scheme '{split_scheme}'.")

        self._x = x
        self._scheme = scheme

        self._is_split = False
        self._split_cfg = None
        if split_scheme is not None:
            split_x = self._to_x(split_node)
            if not (x[0] < split_x < x[-1]):
                raise ValueError(f"split_node {split_x:.6f} must lie strictly inside the domain ({x[0]:.6f}, {x[-1]:.6f}).")
            split_idx = int(np.searchsorted(x, split_x, side="left"))
            self._is_split = True
            self._split_cfg = {
                "scheme": split_scheme,
                "split_x": split_x,
                "split_idx": split_idx,
                "exact": bool(np.isclose(x[split_idx], split_x))
            }


        self._y = None
        self.y = np.asarray(y)


    @property
    def x(self) -> np.ndarray:
        return self._x


    @property
    def y(self) -> np.ndarray:
        return self._y

    @y.setter
    def y(self, value):
        value = np.asarray(value, dtype=float)
        if value.shape != self._x.shape:
            raise ValueError(f"y must have the same shape as x {self._x.shape}; got {value.shape}.")
        self._y = value
        if self._is_split is not None:
            self._build_interpolators()


    @property
    def scheme(self) -> str:
        return self._scheme


    @property
    def split_x(self) -> float | None:
        return self._split_cfg["split_x"] if self._is_split else None


    def interpolate(self, x_star):
        scalar = np.ndim(x_star) == 0
        x_star = np.atleast_1d(np.asarray(x_star, dtype=float))
        out = self._evaluate(x_star)
        return float(out[0]) if scalar else out


    # private functions

    def _to_x(self, node) -> float:
        if isinstance(node, ql.Date):
            return ql.Actual365Fixed().yearFraction(ql.Date.todaysDate(), node)
        return float(node)

    def _build_interpolators(self) -> None:
        if self._y is None or not self._is_split:
            self._interp_L = self._make_interp(self._x, self._y, self._scheme)
            self._interp_R = None
            return

        cfg = self._split_cfg
        split_x = cfg["split_x"]
        split_idx = cfg["split_idx"]
        x_L = self._x[: split_idx + 1]
        y_L = self._y[: split_idx + 1]
        if cfg["exact"]:
            x_anchor = x_L[-1]
            y_anchor = y_L[-1]
        else:
            tmp_L = self._make_interp(x_L, y_L, self._scheme)
            x_anchor = split_x
            y_anchor = float(tmp_L(split_x))

        x_R = np.concatenate([[x_anchor], self._x[split_idx + 1:]])
        y_R = np.concatenate([[y_anchor], self._y[split_idx + 1:]])
        self._interp_L = self._make_interp(x_L, y_L, self._scheme)
        self._interp_R = self._make_interp(x_R, y_R, cfg["scheme"])
        self._split_cfg["x_anchor"] = x_anchor  # cache for _evaluate


    def _evaluate(self, x_star: np.ndarray) -> np.ndarray:
        if not self._is_split:
            return np.asarray(self._interp_L(x_star), dtype=float)

        anchor = self._split_cfg["x_anchor"]
        mask_L = x_star <= anchor
        mask_R = ~mask_L

        out = np.empty_like(x_star)
        if mask_L.any():
            out[mask_L] = np.asarray(self._interp_L(x_star[mask_L]), dtype=float)
        if mask_R.any():
            out[mask_R] = np.asarray(self._interp_R(x_star[mask_R]), dtype=float)

        return out


    #def _apply_extrapolation(self, x_star: np.ndarray, raw: np.ndarray, interp: _Interpolator, x_lo: float | None = None, x_hi: float | None = None) -> np.ndarray:
    #    x_lo = self._x[0] if x_lo is None else x_lo
    #    x_hi = self._x[-1] if x_hi is None else x_hi
    #
    #    if self._extrapolation == "natural":
    #        return raw
    #
    #    lo_mask = x_star < x_lo
    #    hi_mask = x_star > x_hi
    #
    #    if not lo_mask.any() and not hi_mask.any():
    #        return raw
    #
    #    out = raw.copy()
    #
    #    if self._extrapolation == "flat":
    #        if lo_mask.any():
    #            out[lo_mask] = float(interp(x_lo))
    #        if hi_mask.any():
    #            out[hi_mask] = float(interp(x_hi))
    #
    #    elif self._extrapolation == "linear":
    #        eps = (x_hi - x_lo) * 1e-6  # finite-difference nudge for boundary slope
    #        if lo_mask.any():
    #            f0 = float(interp(x_lo))
    #            slope = (float(interp(x_lo + eps)) - f0) / eps
    #            out[lo_mask] = f0 + slope * (x_star[lo_mask] - x_lo)
    #        if hi_mask.any():
    #            fN = float(interp(x_hi))
    #            slope = (fN - float(interp(x_hi - eps))) / eps
    #            out[hi_mask] = fN + slope * (x_star[hi_mask] - x_hi)
    #
    #    return out

    @staticmethod
    def _make_interp(x: np.ndarray, y: np.ndarray, scheme: str) -> _Interpolator:
        if scheme == "linear":
            return interp1d(x, y, kind = "linear", bounds_error = False, fill_value = (y[0], y[-1]), )
        elif scheme == "cubic":
            return CubicSpline(x, y, extrapolate=True)
        elif scheme == "bspline":
            return make_interp_spline(x, y, k=3)
        elif scheme == "pchip":
            return PchipInterpolator(x, y, extrapolate=True)
        elif scheme == "akima":
            return Akima1DInterpolator(x, y, method="akima")
        else:
            raise ValueError(f"Unknown interpolation scheme: '{scheme}'.")


def run_test():
    x = np.array([0, 0.25, 0.5, 0.75, 1.0, 1.5, 2, 3, 4, 5, 7, 10])
    y = np.array([1.0, 0.9940, 0.9880, 0.9820, 0.9760, 0.9640, 0.9510, 0.9220, 0.8890, 0.8530, 0.7820, 0.6950])

    # no split
    engine = InterpolationEngine(x, y, scheme="linear")
    print(engine.interpolate(5.5))  # float, between 1Y and 18M
    print(engine.interpolate([0.51, 1.3, 1.9, 2.1, 5.0]))  # array

    # with split: linear on short end, pchip on long end
    engine_split = InterpolationEngine(x, y, scheme="linear", split_scheme="pchip", split_node=2.0, )
    print(engine_split.interpolate(5.5))
    print(engine_split.interpolate([0.51, 1.3, 1.9, 2.1, 5.0]))


#run_test()