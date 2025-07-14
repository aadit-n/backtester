import itertools
from backtest_engine import backtest
from indicator_engine import get_indicators
import pandas as pd

def grid_search(df, base_configs, long_expr, short_expr, exit_expr):
    best_result = None
    best_config = None

    for config in base_configs:
        param_grid = config['param_grid']
        keys = list(param_grid.keys())
        values = list(param_grid.values())
        all_combinations = list(itertools.product(*values))

        for combo in all_combinations:
            params = dict(zip(keys, combo))
            df_copy = df.copy()

            try:
                outputs = get_indicators(df_copy, {
                    "name": config["name"],
                    "inputs": config["inputs"],
                    "params": params
                })
                for col, series in outputs.items():
                    df_copy[col] = series

                safe_globals = {"df": df_copy, "pd": pd, "len": len, "__builtins__": {}}
                long_signal = eval(long_expr, safe_globals)
                short_signal = eval(short_expr, safe_globals)
                exit_signal = eval(exit_expr, safe_globals)

                result = backtest(df_copy, long_signal, short_signal, exit_signal)

                if best_result is None or result["total_return"] > best_result["total_return"]:
                    best_result = result
                    best_config = {
                        "name": config["name"],
                        "params": params
                    }
            except Exception:
                continue

    return best_result, best_config
