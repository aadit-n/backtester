import tulipy as tp
import pandas as pd
import numpy as np


OUTPUT_MAPPINGS = {
    "di": ["plus_di", "minus_di"],
    "dm": ["plus_dm", "minus_dm"],
    "bbands": ["lower_band", "middle_band", "upper_band"],
    "macd": ["macd", "signal", "histogram"],
    "adosc": ["adosc"],
    "stoch": ["%K", "%D"],
    "stochrsi": ["stochrsi"],
    "sar": ["sar"],
    "ultosc": ["ultosc"],
    "kvo": ["kvo"],
    "vosc": ["vosc"],
    "apo": ["apo"],
    "aroon": ["aroon_up", "aroon_down"],
    "aroonosc": ["aroonosc"],
    "adx": ["adx"],
    "adxr": ["adxr"],
    "ad": ["ad"],
    "ao": ["ao"],
    "atr": ["atr"],
    "bop": ["bop"],
    "cci": ["cci"],
    "cmo": ["cmo"],
    "cvi": ["cvi"],
    "dx": ["dx"],
    "dpo": ["dpo"],
    "emv": ["emv"],
    "fisher": ["fisher", "fisher_signal"],
    "fosc": ["fosc"],
    "linreg": ["linreg"],
    "linregintercept": ["linregintercept"],
    "linregslope": ["linregslope"],
    "marketfi": ["marketfi"],
    "mass": ["mass"],
    "mfi": ["mfi"],
    "minidmi": ["minidmi"],
    "minus_di": ["minus_di"],
    "minus_dm": ["minus_dm"],
    "mom": ["momentum"],
    "msw": ["msw_sine", "msw_lead"],
    "natr": ["natr"],
    "nvi": ["nvi"],
    "obv": ["obv"],
    "plus_di": ["plus_di"],
    "plus_dm": ["plus_dm"],
    "ppo": ["ppo"],
    "pvi": ["pvi"],
    "roc": ["roc"],
    "rocp": ["rocp"],
    "rocr": ["rocr"],
    "rocr100": ["rocr100"],
    "rsi": ["rsi"],
    "sma": ["sma"],
    "tema": ["tema"],
    "trange": ["trange"],
    "trima": ["trima"],
    "trix": ["trix"],
    "tsf": ["tsf"],
    "typprice": ["typprice"],
    "var": ["var"],
    "vhf": ["vhf"],
    "vidya": ["vidya"],
    "vwma": ["vwma"],
    "wad": ["wad"],
    "wilders": ["wilders"],
    "willr": ["willr"],
    "wma": ["wma"],
    "zlema": ["zlema"],
    "avgprice": ["avgprice"],
    "medprice": ["medprice"],
    "wcprice": ["wcprice"],
    "wclprice": ["wclprice"],
    "sum": ["sum"],
    "sub": ["sub"],
}

def get_indicators(df, config):
    name = config["name"].lower()
    params = config["params"]
    inputs = [df[input_col].dropna().values.astype(np.float64) for input_col in config["inputs"]]

    try:
        func = getattr(tp, name)
    except AttributeError:
        raise ValueError(f"Indicator function '{name}' not found in Tulipy")

    result = func(*inputs, **params)

    if isinstance(result, tuple):
        friendly_names = OUTPUT_MAPPINGS.get(name, [f"{name}_{i}" for i in range(len(result))])
        columns = [
            build_col_name(name, params, suffix=friendly_names[i] if i < len(friendly_names) else str(i))
            for i in range(len(result))
        ]
        series_dict = {
            col: pd.Series(res, index=df.index[-len(res):])
            for col, res in zip(columns, result)
        }
    else:
        col_name = build_col_name(name, params)
        series_dict = {
            col_name: pd.Series(result, index=df.index[-len(result):])
        }

    return series_dict

def build_col_name(name: str, params: dict, suffix=None) -> str:
    param_str = "_".join(str(v) for v in params.values())
    base = f"{name.upper()}_{param_str}" if param_str else name.upper()
    if suffix is not None:
        return f"{base}_{suffix}"
    return base
