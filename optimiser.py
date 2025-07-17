import optuna
from backtest_engine import backtest
from indicator_engine import get_indicators
import pandas as pd

def bayesian_optimiser(df, base_configs, long_expr, short_expr, exit_expr, n_trials=50):
    def objective(trial):
        df_copy = df.copy()
        applied_configs = []

        for config in base_configs:
            param_grid = config.get("param_grid", {})
            if not param_grid:
                continue

            sampled_params = {}
            for key, bounds in param_grid.items():
                if isinstance(bounds[0], int) and isinstance(bounds[1], int):
                    sampled_params[key] = trial.suggest_int(f"{config['name']}_{key}", bounds[0], bounds[1])
                else:
                    sampled_params[key] = trial.suggest_float(f"{config['name']}_{key}", bounds[0], bounds[1])

            outputs = get_indicators(df_copy, {
                "name": config["name"],
                "inputs": config["inputs"],
                "params": sampled_params
            })

            for col, series in outputs.items():
                df_copy[col] = series

            applied_configs.append({
                "name": config["name"],
                "params": sampled_params,
                "inputs": config["inputs"]
            })

        try:
            safe_globals = {"df": df_copy, "pd": pd, "len": len, "__builtins__": {}}
            long_signal = eval(long_expr, safe_globals)
            short_signal = eval(short_expr, safe_globals)
            exit_signal = eval(exit_expr, safe_globals)

            result = backtest(df_copy, long_signal, short_signal, exit_signal)
            return result["total_return"]
        except Exception:
            return -float("inf")

    study = optuna.create_study(direction="maximize")
    study.optimize(objective, n_trials=n_trials)

    best_trial = study.best_trial
    df_copy = df.copy()
    best_config = []

    for config in base_configs:
        param_grid = config.get("param_grid", {})
        if not param_grid:
            continue

        sampled_params = {
            key: best_trial.params[f"{config['name']}_{key}"]
            for key in param_grid.keys()
        }

        outputs = get_indicators(df_copy, {
            "name": config["name"],
            "inputs": config["inputs"],
            "params": sampled_params
        })

        for col, series in outputs.items():
            df_copy[col] = series

        best_config.append({
            "name": config["name"],
            "params": sampled_params
        })

    safe_globals = {"df": df_copy, "pd": pd, "len": len, "__builtins__": {}}
    long_signal = eval(long_expr, safe_globals)
    short_signal = eval(short_expr, safe_globals)
    exit_signal = eval(exit_expr, safe_globals)

    result = backtest(df_copy, long_signal, short_signal, exit_signal)
    

    return result, best_config
