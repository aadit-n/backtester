import tulipy as tp
import pandas as pd
import numpy as np

def get_indicators(df, config):
    name = config["name"].lower()
    params = config["params"]
    inputs = [df[input_col].dropna().values for input_col in config["inputs"]]

    try:
        func = getattr(tp, name)
    except AttributeError:
        raise ValueError(f"Indicator function '{name}' not found in Tulipy")

    result = func(*inputs, **params)

    if isinstance(result, tuple):  
        columns = [f"{name.upper()}_{key}_{'_'.join(map(str, params.values()))}" for key in ["upper", "middle", "lower"]]
        series_dict = {
            col: pd.Series(res, index=df.index[-len(res):])
            for col, res in zip(columns, result)
        }
    else:  
        col_name = f"{name.upper()}_{'_'.join(map(str, params.values()))}"
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