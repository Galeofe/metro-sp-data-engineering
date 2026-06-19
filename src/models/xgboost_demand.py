"""
Modelo — XGBoost para Previsão de Demanda de Transporte Público
Split temporal: últimas 20% das horas como teste.
Usa sklearn GradientBoostingRegressor como fallback se xgboost não estiver instalado.
"""
import pandas as pd
import numpy as np
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from utils.logger import get_logger
from config.settings import XGBOOST_PARAMS

log = get_logger("model.xgboost_demand")

_TARGET = "target"
_EXCLUDE = {"hora_ref", "dt_particao"}


def _get_model():
    try:
        from xgboost import XGBRegressor
        params = {k: v for k, v in XGBOOST_PARAMS.items()
                  if k != "early_stopping_rounds"}
        return XGBRegressor(**params, verbosity=0)
    except ImportError:
        log.warning("xgboost não instalado — usando GradientBoostingRegressor (sklearn)")
        from sklearn.ensemble import GradientBoostingRegressor
        return GradientBoostingRegressor(
            n_estimators=200, max_depth=4,
            learning_rate=0.05, random_state=XGBOOST_PARAMS["random_state"]
        )


def train_and_evaluate(df_gold: pd.DataFrame) -> tuple[object, pd.DataFrame, dict]:
    df = df_gold.copy()

    # Remove colunas não numéricas e irrelevantes
    drop_cols = list(_EXCLUDE) + [c for c in df.columns
                                   if df[c].dtype == object]
    feat_cols = [c for c in df.columns
                 if c not in drop_cols and c != _TARGET]

    df = df.dropna(subset=[_TARGET])
    X = df[feat_cols].fillna(0)
    y = df[_TARGET]

    # Split temporal (últimas 20% horas)
    cut = int(len(df) * 0.80)
    X_train, X_test = X.iloc[:cut], X.iloc[cut:]
    y_train, y_test = y.iloc[:cut], y.iloc[cut:]

    model = _get_model()
    model.fit(X_train, y_train)

    y_pred = model.predict(X_test)
    mae  = mean_absolute_error(y_test, y_pred)
    rmse = np.sqrt(mean_squared_error(y_test, y_pred))
    r2   = r2_score(y_test, y_pred)

    metrics = {
        "mae":   round(mae,  4),
        "rmse":  round(rmse, 4),
        "r2":    round(r2,   4),
        "n_train": int(cut),
        "n_test":  int(len(df) - cut),
    }
    log.info("XGBoost Demanda:  MAE=%.4f  RMSE=%.4f  R²=%.4f", mae, rmse, r2)
    log.info("  Treino: %d amostras | Teste: %d amostras", cut, len(df) - cut)

    # Feature importance
    result_df = X_test.copy()
    result_df["y_real"] = y_test.values
    result_df["y_pred"] = y_pred

    # Feature importance (compatível com XGBoost e sklearn)
    if hasattr(model, "feature_importances_"):
        fi = pd.Series(model.feature_importances_, index=feat_cols).sort_values(ascending=False)
        log.info("  Top-5 features: %s", fi.head(5).to_dict())
        metrics["feature_importance"] = fi.head(10).to_dict()

    return model, result_df, metrics
