import numpy as np
from scipy.optimize import least_squares
from scipy.interpolate import BSpline
from scipy.interpolate import interp1d, make_interp_spline
from abc import ABC, abstractmethod
import QuantLib as ql
 
from charlib.curves import pricingobjects
from charlib.maths import interpolation
from charlib.utility import dates
from charlib.curves import instruments
from charlib.curves import pricingobjects


class Curve(ABC):
 
    def __init__(self, reference_date = ql.Date.todaysDate(),
                 nodes: list[ql.Date] | list[float] | None = None,
                 values: list[float] | None = None,
                 interpolation_scheme: str = "linear",
                 split_scheme: str | None = None,
                 split_node: ql.Date | float | None = None) -> None:
        self.reference_date = reference_date
        self.interpolation_scheme = interpolation_scheme
        self.split_scheme = split_scheme
        self.split_node = split_node
        self.interpolation_engine = None
        self._values = None
        self.nodes = nodes
        self.values = values
        #self.interpolation_engine = interpolation.InterpolationEngine(x = self.t, y = self.values, scheme=interpolation_scheme, split_scheme=split_scheme, split_node=split_node)


    def __len__(self):
        return len(self.t)
 
    @property
    def nodes(self):
        return self._nodes
 
    @nodes.setter
    def nodes(self, nodes: list[ql.Date] | list[float] | None) -> None:
        self._nodes = nodes
        if nodes is not None:
            if all(isinstance(n, ql.Date) for n in nodes):
                self.t = [ql.Actual365Fixed().yearFraction(self.reference_date, d) for d in nodes]
            elif all(isinstance(n, float) for n in nodes):
                self.t = list(nodes)
            else:
                raise TypeError("nodes must be a list of ql.Date or a list of floats.")
            self._try_build_engine()
        else:
            self.t = None
 
    @property
    def values(self):
        return self._values
 
    @values.setter
    def values(self, values: list[float] | np.ndarray | None) -> None:
        self._values = values if values is None else np.asarray(values, dtype=float)
        if self._values is not None:
            if self.interpolation_engine is not None:
                # engine already exists — just update y
                self.interpolation_engine.y = self._values
            else:
                self._try_build_engine()
 
    def discount_factor(self, this_date):
        pass
 
    def zero_rate(self, this_date):
        pass
 
    def forward_rate(self, start_date, end_date):
        if isinstance(start_date, (list, tuple, np.ndarray)) != isinstance(end_date, (list, tuple, np.ndarray)):
            raise TypeError(f"start_date and end_date must both be float or ql.Date, or both arrays; got {type(start_date).__name__} vs {type(end_date).__name__}")
        if isinstance(start_date, ql.Date):
            start_date = ql.Actual365Fixed().yearFraction(self.reference_date, start_date)
        elif isinstance(start_date, (list, tuple, np.ndarray)):
            start_date = np.array([ql.Actual365Fixed().yearFraction(self.reference_date, t) if isinstance(t, ql.Date) else float(t) for t in start_date]) 
        if isinstance(end_date, ql.Date):
            end_date = ql.Actual365Fixed().yearFraction(self.reference_date, end_date)
        elif isinstance(end_date, (list, tuple, np.ndarray)):
            end_date = np.array([ql.Actual365Fixed().yearFraction(self.reference_date, t) if isinstance(t, ql.Date) else float(t) for t in end_date]) 
        return (self.discount_factor(start_date) / self.discount_factor(end_date) - 1.0) / ((np.array(end_date) - np.array(start_date)))
 
    def instantaneous_forward_rate(self, this_date, dt = 1.0/365.0):
        if isinstance(this_date, ql.Date):
            this_date = ql.Actual365Fixed().yearFraction(self.reference_date, this_date)
        elif isinstance(this_date, (list, tuple, np.ndarray)):
            this_date = np.array([ql.Actual365Fixed().yearFraction(self.reference_date, t) if isinstance(t, ql.Date) else float(t) for t in this_date])
        dfs = self.discount_factor(this_date)
        dfs_bumped = self.discount_factor(this_date + float(dt))
        fwd = (np.log(dfs) - np.log(dfs_bumped)) / float(dt)
        return fwd.item() if fwd.size == 1 else fwd


    def _try_build_engine(self) -> None:
        """Build the interpolation engine once both t and values are available."""
        if self.t is not None and self._values is not None:
            self.interpolation_engine = interpolation.InterpolationEngine(
                x=self.t,
                y=self.values,
                scheme=self.interpolation_scheme,
                split_scheme=self.split_scheme,

                split_node=self.split_node,
            )

    def _to_t(self, date_or_t) -> float | np.ndarray:
        if isinstance(date_or_t, ql.Date):
            return ql.Actual365Fixed().yearFraction(self.reference_date, date_or_t)
        elif isinstance(date_or_t, (list, tuple, np.ndarray)):
            return np.array([
                ql.Actual365Fixed().yearFraction(self.reference_date, t) if isinstance(t, ql.Date) else float(t)
                for t in date_or_t
            ])
        return float(date_or_t)
 
 
class BaseCurve(Curve):
 
    def __init__(self, reference_date = ql.Date.todaysDate(),
                 nodes: list[ql.Date] | list[float] | None = None,
                 dfs: list[float] | None = None,
                 interpolation_scheme: str = "linear",
                 split_scheme: str | None = None,
                 split_node: ql.Date | float | None = None) -> None:
        super().__init__(reference_date=reference_date, nodes=nodes, values=dfs, interpolation_scheme=interpolation_scheme, split_scheme=split_scheme, split_node=split_node)
        if dfs is None:
            if self.nodes is not None:
                self.dfs = np.exp(-0.03 * np.array(self.t))
            else:
                self.dfs = None
        elif self.nodes is None:
            raise TypeError(f"Cannot provide dfs without nodes")
        else:
            self.dfs = dfs
 
    @property
    def dfs(self):
        return self._dfs
 
    @dfs.setter
    def dfs(self, dfs):
        self._dfs = dfs
        if self._dfs is not None:
            self.values = np.log(dfs)
        else:
            self.values = dfs
 
    def discount_factor(self, this_date):
        if isinstance(this_date, ql.Date):
            this_date = ql.Actual365Fixed().yearFraction(self.reference_date, this_date)
        elif isinstance(this_date, (list, tuple, np.ndarray)):
            this_date = np.array([ql.Actual365Fixed().yearFraction(self.reference_date, t) if isinstance(t, ql.Date) else float(t) for t in this_date])
        df = self.interpolation_engine.interpolate(this_date)
        return np.exp(df)
 
    def zero_rate(self, this_date):
        if isinstance(this_date, ql.Date):
            this_date = ql.Actual365Fixed().yearFraction(self.reference_date, this_date)
        df = self.discount_factor(this_date)
        z = -np.log(df) / this_date
        return z
 
 
class SpreadCurve(Curve):

    def __init__(self, reference_date=ql.Date.todaysDate(),
                 base_curve: BaseCurve | None = None,
                 nodes: list[ql.Date] | list[float] | None = None,
                 spreads: list[float] | None = None,
                 interpolation_scheme: str = "linear",
                 split_scheme: str | None = None,
                 split_node: ql.Date | float | None = None) -> None:
        super().__init__(reference_date=reference_date, nodes=nodes, values=spreads, interpolation_scheme=interpolation_scheme, split_scheme=split_scheme, split_node=split_node)
        self.base_curve = base_curve
        if spreads is None:
            if self.nodes is not None:
                self.spreads = np.exp(-0.001 * np.array(self.t))
            else:
                self.spreads = None
        elif self.nodes is None:
            raise TypeError(f"Cannot provide dfs without nodes")
        else:
            self.spreads = spreads
 
    @property
    def spreads(self):
        return self._spreads
 
    @spreads.setter
    def spreads(self, spreads):
        self._spreads = spreads
        if self._spreads is not None:
            self.values = np.log(spreads)
        else:
            self.values = spreads
 
    def discount_factor(self, this_date):
        if isinstance(this_date, ql.Date):
            this_date = ql.Actual365Fixed().yearFraction(self.reference_date, this_date)
        elif isinstance(this_date, (list, tuple, np.ndarray)):
            this_date = np.array([ql.Actual365Fixed().yearFraction(self.reference_date, t) if isinstance(t, ql.Date) else float(t) for t in this_date])
        return self.base_curve.discount_factor(this_date) * np.exp(self.interpolation_engine.interpolate(this_date))
 
    def zero_rate(self, this_date):
        raise NotImplementedError('This curve is for forecasting forward rates only')
 
 
class CurvesSet:
 
    def __init__(self, reference_date: ql.Date | None = ql.Date.todaysDate(), curves_definitions: dict | None = None):
        self.reference_date = reference_date
        self.curves_mapping = None
        self.calibration_basket = None
        self.jacobian_matrix = None
        self.iter = 0
        self.n = 0
        self.splits = None
        self.theta = None
        self.q_old = None

        self.curves_mapping, self.calibration_basket = self._set_up_calibration(curves_definitions)


    def __getitem__(self, this_curve):
        return self.get_curve(this_curve)


    def __getattr__(self, this_curve):
        if this_curve != "curves_mapping" and self.curves_mapping is not None and this_curve in self.curves_mapping:
            return self.curves_mapping[this_curve]
        raise AttributeError(f"'{type(self).__name__}' object has no attribute '{this_curve}'")


    def __contains__(self, key):
        return key in self.curves_mapping


    def __len__(self):
        return len(self.curves_mapping)


    def __iter__(self):
        return iter(self.curves_mapping)


    def keys(self):
        return self.curves_mapping.keys()


    def items(self):
        return self.curves_mapping.items()


    def get_curve(self, this_curve):
        return self.curves_mapping[this_curve]


    def map_curves(self, trade_mapping):
        return {key: self.curves_mapping[value] for key, value in trade_mapping.items()}


    def _set_up_calibration(self, curves_definitions: dict):
        spot_date = dates.parse_date('1b', self.reference_date)
        curves_mapping = {}
        basket = {}
        constraints = None

        for curve_key, cfg in curves_definitions.items():
            pillars_dates = [dates.parse_date(t, spot_date) for t in cfg['pillars']]
            scheme = cfg.get('scheme', 'linear')
            split_scheme = cfg.get('split_scheme', None)
            if cfg.get('split_node', None) != None:
                split_node = dates.parse_date(cfg.get('split_node'), spot_date)
            else:
                split_node = None

            if "base_curve" in cfg:
                base_key = cfg["base_curve"]
                if base_key not in curves_mapping:
                    raise ValueError(f"base_curve '{base_key}' for '{curve_key}' has not been built yet.")
                curves_mapping[curve_key] = SpreadCurve(reference_date=self.reference_date, base_curve=curves_mapping[base_key], nodes=pillars_dates, interpolation_scheme=scheme, split_scheme=split_scheme, split_node=split_node)
            else:
                curves_mapping[curve_key] = BaseCurve(reference_date=self.reference_date, nodes=pillars_dates, interpolation_scheme=scheme, split_scheme=split_scheme, split_node=split_node)

            for inst_name, inst_cfg in cfg["instruments"].items():
                if inst_name not in instruments.instruments_definitions:
                    raise KeyError(f"Instrument '{inst_name}' not found in instruments registry.")
                if inst_cfg['include']:
                    inst_def = instruments.instruments_definitions[inst_name]
                    pricing_object = instruments.create_pricing_object_from_convention(start_date = inst_def['start_date'], end_date = inst_def['end_date'], notional=1, convention = inst_def['convention'])
                    basket[inst_name] = {
                        'object': pricing_object,
                        'quote': 0,
                        'weight': inst_cfg['weight'],
                        'include': inst_cfg['include'],
                        'ticker': inst_def['ticker'],
                    }

            constraints = None
            constraints_cfg = cfg.get("constraints", None)
            if constraints_cfg is not None:
                constraints = {}
                for constraint_name, constraint_cfg in constraints_cfg.items():
                    pricing_objects = []
                    for inst_name in constraint_cfg["instruments"]:
                        if inst_name not in instruments.instruments_definitions:
                            raise KeyError(f"Instrument '{inst_name}' not found in instruments registry.")
                        if inst_name in basket:
                            pricing_objects.append(basket[inst_name]['object'])
                        else:
                            inst_def = instruments.instruments_definitions[inst_name]
                            pricing_objects.append(
                                instruments.create_pricing_object_from_convention(
                                    start_date=inst_def['start_date'],
                                    end_date=inst_def['end_date'],
                                    notional=1,
                                    convention=inst_def['convention'],
                                )
                            )
                    constraints[constraint_name] = {
                        'object': instruments.create_constraint(pricing_objects),
                        'quote': constraint_cfg['value'],
                        'weight': constraint_cfg['weight'],
                        'include': constraint_cfg['include'],
                    }
                basket = {**basket, **constraints}

        return curves_mapping, CalibrationBasket(basket)


    def calibrate(self, fast_rebuild_mode = False):
        #self.calibration_basket = calibration_basket.subset_basket
        if self.jacobian_matrix is None or fast_rebuild_mode is False:
            theta = self.full_calibration()
        else:
            theta = self.fast_calibration()
        solving_values_tmp = np.split(theta, self.splits)
        for (key, curve), x in zip(self.curves_mapping.items(), solving_values_tmp):
            self._unpack_solving_values(curve, x)


    def full_calibration(self):
        self.iter = 1
        self.n = [(len(value) - 1) for value in self.curves_mapping.values()]
        self.splits = np.cumsum(self.n)[:-1]
        solving_values = np.concatenate([self._pack_solving_values(curve) for key, curve in self.curves_mapping.items()]) 
        res = least_squares(self.objective_function, solving_values, method='lm', ftol=1e-12, xtol=1e-12, gtol=1e-12)
        theta = res.x
        self.theta = theta
        self.jacobian_matrix = res.jac
        self.q_old = [value['quote'] for key, value in self.calibration_basket.items()]
        return theta


    def fast_calibration(self):
        # Currently, there is no check re size of the Jacobian vs size of instruments.
        # Also there is no check re tolerance vs market move
        print('i am faaaaaast!!!')
        q_new = [value['quote'] for key, value in self.calibration_basket.items()]
        d_q = np.array(q_new) - np.array(self.q_old)
        lam = 1e-10
        delta = np.linalg.solve(self.jacobian_matrix.T @ self.jacobian_matrix + lam * np.eye(self.jacobian_matrix.shape[1]), self.jacobian_matrix.T @ d_q)
        theta = self.theta + delta
        return theta


    def objective_function(self, solving_values):
        solving_values_tmp = np.split(solving_values, self.splits)
        for (key, curve), x in zip(self.curves_mapping.items(), solving_values_tmp):
            self._unpack_solving_values(curve, x)
        fit = []
        for key, value in self.calibration_basket.items():
            print(f"key: {key} market: {value['quote']} model: {value['object'].implied_rate_spread(self)}")
            fit.append(np.sqrt(value['weight']) * (value['object'].implied_rate_spread(self) - value['quote']))
        obj = fit
        self.iter += 1
        return obj


    def calibration_results(self):
        res = {}
        for key, value in self.calibration_basket.items():
            x = value['object'].implied_rate_spread(self)
            res[key] = {'market': value['quote'], 'model': round(float(x), 5), 'diff': round(float((x - value['quote'])),5)}
        return res


    @staticmethod
    def _pack_solving_values(this_curve):
        if isinstance(this_curve, BaseCurve):
            return this_curve.dfs[1:]
        elif isinstance(this_curve, SpreadCurve):
            return this_curve.spreads[1:]
        else:
            raise TypeError(f"Must give a BaseCurve or a SpreadCurve; got {type(this_curve).__name__}")


    @staticmethod
    def _unpack_solving_values(this_curve, this_array):
        if isinstance(this_curve, BaseCurve):
            this_curve.dfs = np.concatenate(([1.0], this_array))
        elif isinstance(this_curve, SpreadCurve):
            this_curve.spreads = np.concatenate(([1.0], this_array))
        else:
            raise TypeError(f"Must give a BaseCurve or a SpreadCurve; got {type(this_curve).__name__}")


class CalibrationBasket:
 
    def __init__(self, basket):
        self.basket = basket
        self.tickers = {}
        self.set_bloomberg_tickers()
        ##for key, value in self.basket.items():
        #    value.update({'object': utility.create_pricing_object_from_convention(value['start'], value['end'], 1, value['convention'])})
        #self.constraints = constraints
        #if self.constraints is not None:
        #    for key, value in self.constraints.items():
        #        value.update({'object': utility.create_constraint([self.basket[x]['object'] for x in value['constraint']])})
        #    self.full_basket = {**self.basket, **self.constraints}
        #else:
        #    self.full_basket = self.basket
        #self.subset_basket = {key: {'object': value['object'], 'quote': value['quote'], 'weight': value['weight']} for key, value in self.full_basket.items() if value.get('include') == True}


    def __getitem__(self, key):
        return self.basket[key]


    def __setitem__(self, key, value):
        self.basket[key] = value


    def __contains__(self, key):
        return key in self.basket


    def __len__(self):
        return len(self.basket)


    def __iter__(self):
        return iter(self.basket)


    def keys(self):
        return self.basket.keys()


    def values(self):
        return self.basket.values()


    def items(self):
        return self.basket.items()


    def set_bloomberg_tickers(self):
        for key, value in self.basket.items():
            if 'ticker' in value:
                self.tickers[key] = value['ticker']


    def set_market_quotes(self, market_quotes: dict) -> None:
        for key, value in market_quotes.items():
            self.basket[key]['quote'] = market_quotes[key]


    def get_market_quotes(self):
        # Used on subset_basket for the fast calibration
        return [value['quote'] for key, value in self.subset_basket.items()]


    def price_all(self, curves_set):
        return [value['object'].implied_rate_spread(curves_set) for key, value in self.basket.items()]






def run_test():
    import matplotlib.pyplot as plt
    curves_definitions = {
      "AUD": {
        "aud.aonia.1d": {
          "instruments": {
            "aud_cash_1d":  {"include": True, "weight": 1},
                "aud_ois_rba2": {"include": True, "weight": 1},
                #"aud_ib_1":     {"include": False, "weight": 1},
                #"aud_ib_2":     {"include": True, "weight": 1},
                "aud_ib_3":     {"include": True, "weight": 1},
                "aud_ib_4":     {"include": True, "weight": 1},
                "aud_ib_5":     {"include": True, "weight": 1},
                "aud_ib_6":     {"include": True, "weight": 1},
                "aud_ib_7":     {"include": True, "weight": 1},
                "aud_ib_8":     {"include": True, "weight": 1},
                "aud_ib_9":     {"include": True, "weight": 1},
                "aud_ib_10":    {"include": True, "weight": 1},
                "aud_ib_11":    {"include": True, "weight": 1},
                "aud_ib_12":    {"include": True, "weight": 1},
                #"aud_bob_1y":   {"include": True, "weight": 1},
                "aud_bob_18m":  {"include": True, "weight": 1},
                "aud_bob_2y":   {"include": True, "weight": 1},
                "aud_bob_3y":   {"include": True, "weight": 1}
          },
            "constraints": {
                #"cash_rba1_rba2": {"instruments": ["aud_cash_1d", "aud_ois_rba1", "aud_ois_rba2"], "value": 0, "include": True, "weight": 0.001},
                #"rba1_rba2_rba3": {"instruments": ["aud_ois_rba1", "aud_ois_rba2", "aud_ois_rba3"], "value": 0, "include": True, "weight": 0.001},
                "rba2_rba3_rba4": {"instruments": ["aud_ois_rba2", "aud_ois_rba3", "aud_ois_rba4"], "value": 0, "include": True, "weight": 0.001},
                "rba3_rba4_rba5": {"instruments": ["aud_ois_rba3", "aud_ois_rba4", "aud_ois_rba5"], "value": 0, "include": True, "weight": 0.001},
                "rba4_rba5_rba6": {"instruments": ["aud_ois_rba4", "aud_ois_rba5", "aud_ois_rba6"], "value": 0, "include": True, "weight": 0.001},
                "rba5_rba6_rba7": {"instruments": ["aud_ois_rba5", "aud_ois_rba6", "aud_ois_rba7"], "value": 0, "include": True, "weight": 0.001},
                "rba6_rba7_rba8": {"instruments": ["aud_ois_rba6", "aud_ois_rba7", "aud_ois_rba8"], "value": 0, "include": True, "weight": 0.001},
            },
            "pillars": [ql.Date.todaysDate(), "rba2", "rba3", "rba4", "rba5", "rba6", "rba7", "rba8"],
            "scheme": "linear",
            #"split_scheme": "bspline",
            #"split_node": dates.parse_date("rba8"),
        },

        "aud.bbsw.3m": {
          "instruments": {
                "aud_bill_3m":	{"include": True, "weight": 1},
                "aud_sfe_1":    {"include": True, "weight": 1},
                "aud_sfe_2":    {"include": True, "weight": 1},
                "aud_sfe_3":    {"include": True, "weight": 1},
                "aud_sfe_4":    {"include": True, "weight": 1},
                "aud_sfe_5":    {"include": True, "weight": 1},
                "aud_sfe_6":    {"include": True, "weight": 1},
                "aud_sfe_7":    {"include": True, "weight": 1},
                "aud_sfe_8":    {"include": True, "weight": 1},
                "aud_irs_3y":   {"include": True, "weight": 1}
          },
            "pillars": [ql.Date.todaysDate(), "sfe1", "sfe2", "sfe3", "sfe4", "sfe5", "sfe6", "sfe7", "sfe8", "sfe9", "3y"],
            "base_curve": "aud.aonia.1d",
            "interpolation": "bspline",
        }
      }
    }

    quotes = {
        'aud_cash_1d': 0.0385,
        "aud_ois_rba2": 0.04,
        #'aud_ib_2': 95.98,
        'aud_ib_3': 95.835,
        'aud_ib_4': 95.785,
        'aud_ib_5': 95.755,
        'aud_ib_6': 95.66,
        'aud_ib_7': 95.60,
        'aud_ib_8': 95.54,
        'aud_ib_9': 95.475,
        'aud_ib_10': 95.46,
        'aud_ib_11': 95.46,
        'aud_ib_12': 95.46,
        #'aud_bob_1y': 15/10000.0,
        'aud_bob_18m': 1 / 10000.0,
        'aud_bob_2y': 1 / 10000.0,
        'aud_bob_3y': 1 / 10000.0,
        "aud_bill_3m": 0.045,
        "aud_sfe_1": 95,
        "aud_sfe_2": 95,
        "aud_sfe_3": 95,
        "aud_sfe_4": 95,
        "aud_sfe_5": 95,
        "aud_sfe_6": 95,
        "aud_sfe_7": 95,
        "aud_sfe_8": 95,
        "aud_irs_3y": 0.05,
    }

    curves_definitions = curves_definitions["AUD"]
    my_curves_set = CurvesSet(reference_date=ql.Date.todaysDate(), curves_definitions=curves_definitions)
    bbg_tickers = my_curves_set.calibration_basket.tickers
    print(bbg_tickers)
    #print(my_curves_set.calibration_basket.basket)
    #print(my_curves_set.calibration_basket.price_all(my_curves_set))

    a = instruments.create_pricing_object_from_convention("1b", "1y", 1, 'aud.tbs.qq.aonia.bbsw.aonia')
    print(a.start_date)
    print(a.end_date)
    print(a.implied_rate_spread(my_curves_set))

    my_curves_set.calibration_basket.set_market_quotes(quotes)
    #my_curves_set.calibrate()
    t = np.arange(0, 1 + 1 / 365, 1 / 365)
    fwds = my_curves_set['aud.aonia.1d'].forward_rate(t[:-1], t[1:])

    plt.plot(t[:-1], fwds)
    plt.grid(True)
    plt.show()

    #start = np.arange(0, 3, 1 / 365)
    #end = start + 3 / 12
    #fwds_3m = my_curves_set['aud.bbsw.3m'].forward_rate(start, end)
    #plt.plot(start, fwds_3m)
    #plt.grid(True)
    #plt.show()

    #a = pricingobjects.Future("bom1", "eom1", {'forecasting_curve': 'aud.aonia.1d'})
    #print(a.price(my_curves_set))

run_test()