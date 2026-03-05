import numpy as np
from scipy.optimize import least_squares
from scipy.interpolate import BSpline
from scipy.interpolate import interp1d, make_interp_spline
from abc import ABC, abstractmethod
import QuantLib as ql
 
from charlib.utility import utility
from charlib.maths import interpolation
 
 
class Curve(ABC):
 
    def __init__(self, reference_date = ql.Date.todaysDate(), nodes = None, values = None, params = None):
        self.interpolation_engine = None
        self.reference_date = reference_date
        self.nodes = nodes
        self.values = values
        self.params = params
        if self.params is not None:
            self.interpolation_engine = interpolation.InterpolationEngine(x = self.t, y = self.values, scheme=params['scheme'], split_interpolation=params['split_interpolation'])
 
    def __len__(self):
        return len(self.t)
 
    @property
    def nodes(self):
        return self._nodes
 
    @nodes.setter
    def nodes(self, nodes):
        self._nodes = nodes
        if self._nodes is not None:
            self.t = [ql.Actual365Fixed().yearFraction(self.reference_date, d) for d in self._nodes]
 
    @property
    def values(self):
        return self._values
 
    @values.setter
    def values(self, values):
        self._values = values
        if self._values is not None and self.interpolation_engine is not None:
            self.interpolation_engine.y = self._values
 
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
 
 
class OutrightCurve(Curve):
 
    def __init__(self, reference_date = ql.Date.todaysDate(), nodes = None, dfs = None, params = None):
        super().__init__(reference_date=reference_date, nodes=nodes, values=dfs, params=params)
        if dfs is None:
            if self.nodes is not None:
                self.dfs = np.exp([-0.03] * np.array(self.t))
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
 
    def __init__(self, reference_date = ql.Date.todaysDate(), outright_curve = OutrightCurve(), nodes = None, spreads = None, params = None):
        super().__init__(reference_date=reference_date, nodes=nodes, values=spreads, params=params)
        self.outright_curve = outright_curve
        if spreads is None:
            if self.nodes is not None:
                #self.spreads = [0] * len(self.nodes)
                self.spreads = np.exp([-0.001] * np.array(self.t))
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
        # self._spreads = spreads
        # self.values = spreads
        self._spreads = spreads
        if self._spreads is not None:
            self.values = np.log(spreads)
        else:
            self.values = spreads
 
    def discount_factor(self, this_date):
        #raise NotImplementedError('This curve is for forecasting forward rates only')
        if isinstance(this_date, ql.Date):
            this_date = ql.Actual365Fixed().yearFraction(self.reference_date, this_date)
        elif isinstance(this_date, (list, tuple, np.ndarray)):
            this_date = np.array([ql.Actual365Fixed().yearFraction(self.reference_date, t) if isinstance(t, ql.Date) else float(t) for t in this_date])
        return self.outright_curve.discount_factor(this_date) * np.exp(self.interpolation_engine.interpolate(this_date))
 
    def zero_rate(self, this_date):
        raise NotImplementedError('This curve is for forecasting forward rates only')
 
 
class CurvesSet:
 
    def __init__(self, curves_mapping):
        self.curves_mapping = curves_mapping
        self.jacobian_matrix = None
 
    def __getitem__(self, this_curve):
        return self.get_curve(this_curve)
 
    def __getattr__(self, this_curve):
        return self.curves_mapping[this_curve]
 
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
 
    def calibrate(self, calibration_basket, fast_rebuild_mode = False):
        self.calibration_basket = calibration_basket.subset_basket
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
        tmp = np.linalg.solve(self.jacobian_matrix.T @ self.jacobian_matrix + lam * np.eye(self.jacobian_matrix.shape[1]), self.jacobian_matrix.T @ d_q)
        theta = self.theta + np.linalg.solve(self.jacobian_matrix.T @ self.jacobian_matrix + lam * np.eye(self.jacobian_matrix.shape[1]), self.jacobian_matrix.T @ d_q)
        return theta
 
    def objective_function(self, solving_values):
        #print(self.iter)
        solving_values_tmp = np.split(solving_values, self.splits)
        for (key, curve), x in zip(self.curves_mapping.items(), solving_values_tmp):
            self._unpack_solving_values(curve, x)
        fit = []
        for key, value in self.calibration_basket.items():
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
 
    def _pack_solving_values(self, this_curve):
        if isinstance(this_curve, OutrightCurve):
            return this_curve.dfs[1:]
        elif isinstance(this_curve, SpreadCurve):
            #return this_curve.spreads
            return this_curve.spreads[1:]
        else:
            TypeError(f"Must give an OutrightCurve or a SpreadCurve; got {type(this_curve).__name__}")
 
    def _unpack_solving_values(self, this_curve, this_array):
        if isinstance(this_curve, OutrightCurve):
            this_curve.dfs = np.concatenate(([1.0], this_array))
        elif isinstance(this_curve, SpreadCurve):
            #this_curve.spreads = this_array
            this_curve.spreads = np.concatenate(([1.0], this_array))
        else:
            TypeError(f"Must give an OutrightCurve or a SpreadCurve; got {type(this_curve).__name__}")
 
 
class CalibrationBasket():
 
    def __init__(self, basket, constraints=None):
        self.basket = basket
        for key, value in self.basket.items():
            value.update({'object': utility.create_pricing_object_from_convention(value['start'], value['end'], 1, value['convention'])})
        self.constraints = constraints
        if self.constraints is not None:
            for key, value in self.constraints.items():
                value.update({'object': utility.create_constraint([self.basket[x]['object'] for x in value['constraint']])})
            self.full_basket = {**self.basket, **self.constraints}
        else:
            self.full_basket = self.basket
        self.subset_basket = {key: {'object': value['object'], 'quote': value['quote'], 'weight': value['weight']} for key, value in self.full_basket.items() if value.get('include') == True}
 
    def get_market_quotes(self):
        # Used on subset_basket for the fast calibration
        return [value['quote'] for key, value in self.subset_basket.items()]
 
    def price_all(self, curvesSet):
        return [value['object'].implied_rate_spread(curvesSet) for key, value in self.full_basket.items()]


