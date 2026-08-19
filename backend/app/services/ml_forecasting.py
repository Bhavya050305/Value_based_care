"""ML Forecasting Engine with 3-Model Training & Evaluation (Random Forest, Gradient Boosting, Ridge)."""

import numpy as np
import pandas as pd
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from fastapi import HTTPException
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.linear_model import Ridge
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score


_CACHE = {}

class MLForecastingService:
    """Trains ML algorithms on historical ACO database metrics from aco_performance_* tables and generates predictions."""

    async def get_aco_forecast(self, db: AsyncSession, aco_id: str, target_year: int = 2025) -> dict:
        cache_key = f"{aco_id}_{target_year}"
        if cache_key in _CACHE:
            return _CACHE[cache_key]

        # Load historical records for target ACO directly from aco_performance_* tables
        stmt = text("""
            SELECT 2022 AS year, "ACO_ID", "ABtotBnchmk", "ABtotExp", "GenSaveLoss", 
                   "BenchmarkPMPM", "PMPM", "SavingsLossPct", "QualScore", "N_AB", "ADM", "P_EDV_Vis"
            FROM public.aco_performance_2022 WHERE "ACO_ID" = :aco_id
            UNION ALL
            SELECT 2023 AS year, "ACO_ID", "ABtotBnchmk", "ABtotExp", "GenSaveLoss", 
                   "BenchmarkPMPM", "PMPM", "SavingsLossPct", "QualScore", "N_AB", "ADM", "P_EDV_Vis"
            FROM public.aco_performance_2023 WHERE "ACO_ID" = :aco_id
            UNION ALL
            SELECT 2024 AS year, "ACO_ID", "ABtotBnchmk", "ABtotExp", "GenSaveLoss", 
                   "BenchmarkPMPM", "PMPM", "SavingsLossPct", "QualScore", "N_AB", "ADM", "P_EDV_Vis"
            FROM public.aco_performance_2024 WHERE "ACO_ID" = :aco_id
            ORDER BY year ASC;
        """)
        res = await db.execute(stmt, {"aco_id": aco_id})
        aco_rows = res.fetchall()

        if not aco_rows or len(aco_rows) < 2:
            raise HTTPException(
                status_code=400,
                detail="Insufficient historical data to generate a reliable forecast."
            )

        cols = ["year", "ACO_ID", "ABtotBnchmk", "ABtotExp", "GenSaveLoss", "BenchmarkPMPM", "PMPM", "SavingsLossPct", "QualScore", "N_AB", "ADM", "P_EDV_Vis"]
        aco_df = pd.DataFrame(aco_rows, columns=cols)
        
        for num_col in ["ABtotBnchmk", "ABtotExp", "GenSaveLoss", "BenchmarkPMPM", "PMPM", "SavingsLossPct", "QualScore", "N_AB", "ADM", "P_EDV_Vis"]:
            aco_df[num_col] = pd.to_numeric(aco_df[num_col], errors='coerce').fillna(0.0)

        source_years = [int(y) for y in aco_df["year"].tolist()]

        # Query full dataset across all ACOs for robust ML model training
        all_stmt = text("""
            SELECT 2022 AS year, "ACO_ID", "ABtotBnchmk", "ABtotExp", "GenSaveLoss", 
                   "BenchmarkPMPM", "PMPM", "SavingsLossPct", "QualScore", "N_AB", "ADM", "P_EDV_Vis"
            FROM public.aco_performance_2022
            UNION ALL
            SELECT 2023 AS year, "ACO_ID", "ABtotBnchmk", "ABtotExp", "GenSaveLoss", 
                   "BenchmarkPMPM", "PMPM", "SavingsLossPct", "QualScore", "N_AB", "ADM", "P_EDV_Vis"
            FROM public.aco_performance_2023
            UNION ALL
            SELECT 2024 AS year, "ACO_ID", "ABtotBnchmk", "ABtotExp", "GenSaveLoss", 
                   "BenchmarkPMPM", "PMPM", "SavingsLossPct", "QualScore", "N_AB", "ADM", "P_EDV_Vis"
            FROM public.aco_performance_2024;
        """)
        all_res = await db.execute(all_stmt)
        all_rows = all_res.fetchall()
        full_df = pd.DataFrame(all_rows, columns=cols)
        for num_col in ["ABtotBnchmk", "ABtotExp", "GenSaveLoss", "BenchmarkPMPM", "PMPM", "SavingsLossPct", "QualScore", "N_AB", "ADM", "P_EDV_Vis"]:
            full_df[num_col] = pd.to_numeric(full_df[num_col], errors='coerce').fillna(0.0)

        features = ["year", "BenchmarkPMPM", "PMPM", "QualScore", "N_AB", "ADM", "P_EDV_Vis"]
        target = "GenSaveLoss"

        df_train = full_df[full_df["year"] < 2024]
        df_val = full_df[full_df["year"] == 2024]

        X_train, y_train = df_train[features], df_train[target]
        X_val, y_val = df_val[features], df_val[target]

        # Fast hyperparameter configuration (30 trees, max_depth=5)
        rf_model = RandomForestRegressor(n_estimators=30, max_depth=5, random_state=42)
        rf_model.fit(X_train, y_train)
        rf_preds = rf_model.predict(X_val)
        rf_mae = float(mean_absolute_error(y_val, rf_preds))
        rf_rmse = float(np.sqrt(mean_squared_error(y_val, rf_preds)))
        rf_r2 = float(r2_score(y_val, rf_preds))

        gb_model = GradientBoostingRegressor(n_estimators=30, max_depth=3, random_state=42)
        gb_model.fit(X_train, y_train)
        gb_preds = gb_model.predict(X_val)
        gb_mae = float(mean_absolute_error(y_val, gb_preds))
        gb_rmse = float(np.sqrt(mean_squared_error(y_val, gb_preds)))
        gb_r2 = float(r2_score(y_val, gb_preds))

        ridge_model = Ridge(alpha=1.0)
        ridge_model.fit(X_train, y_train)
        ridge_preds = ridge_model.predict(X_val)
        ridge_mae = float(mean_absolute_error(y_val, ridge_preds))
        ridge_rmse = float(np.sqrt(mean_squared_error(y_val, ridge_preds)))
        ridge_r2 = float(r2_score(y_val, ridge_preds))

        model_evals = [
            {"modelName": "Gradient Boosting Regressor", "mae": gb_mae, "rmse": gb_rmse, "r2Score": round(gb_r2, 4), "isWinner": False, "modelObj": gb_model},
            {"modelName": "Random Forest Regressor", "mae": rf_mae, "rmse": rf_rmse, "r2Score": round(rf_r2, 4), "isWinner": False, "modelObj": rf_model},
            {"modelName": "Ridge Regression", "mae": ridge_mae, "rmse": ridge_rmse, "r2Score": round(ridge_r2, 4), "isWinner": False, "modelObj": ridge_model},
        ]
        model_evals.sort(key=lambda x: x["mae"])
        model_evals[0]["isWinner"] = True
        best_model = model_evals[0]["modelObj"]

        # Clean model evals list for json serialization
        clean_evals = [
            {"modelName": m["modelName"], "mae": m["mae"], "rmse": m["rmse"], "r2Score": m["r2Score"], "isWinner": m["isWinner"]}
            for m in model_evals
        ]


        last_row = aco_df.iloc[-1]
        last_bm_pmpm = float(last_row["BenchmarkPMPM"])
        last_pmpm = float(last_row["PMPM"])
        last_qual = float(last_row["QualScore"])
        last_members = int(last_row["N_AB"])
        last_adm = float(last_row["ADM"])
        last_ed = float(last_row["P_EDV_Vis"])

        pred_features = pd.DataFrame([{
            "year": target_year,
            "BenchmarkPMPM": last_bm_pmpm,
            "PMPM": last_pmpm * 0.985,
            "QualScore": min(100.0, last_qual + 0.5),
            "N_AB": last_members,
            "ADM": last_adm * 0.97,
            "P_EDV_Vis": last_ed * 0.97
        }])[features]

        pred_gen_save = float(best_model.predict(pred_features)[0])
        pred_savings_pct = round((pred_gen_save / max(1.0, last_bm_pmpm * last_members * 12)) * 100.0, 2)
        pred_pmpm = round(last_pmpm * 0.985, 2)
        pred_bm_pmpm = round(last_bm_pmpm * 1.02, 2)
        pred_qual = min(100.0, round(last_qual + 0.6, 1))

        historical_series = []
        for idx, row in aco_df.iterrows():
            yr = int(row["year"])
            historical_series.append({
                "year": yr,
                "savingsLoss": round(float(row["GenSaveLoss"]), 2),
                "savingsRate": round(float(row["SavingsLossPct"]), 2),
                "pmpm": round(float(row["PMPM"]), 2),
                "benchmarkPmpm": round(float(row["BenchmarkPMPM"]), 2),
                "qualityScore": round(float(row["QualScore"]), 1),
                "isPredicted": False
            })

        combined_series = list(historical_series)
        combined_series.append({
            "year": target_year,
            "savingsLoss": round(pred_gen_save, 2),
            "savingsRate": pred_savings_pct,
            "pmpm": pred_pmpm,
            "benchmarkPmpm": pred_bm_pmpm,
            "qualityScore": pred_qual,
            "isPredicted": True
        })

        result = {
            "forecastTarget": "Gross Savings / Loss (GenSaveLoss)",
            "acoId": aco_id,
            "sourceYears": source_years,
            "forecastYear": target_year,
            "forecastValue": round(pred_gen_save, 2),
            "historicalData": historical_series,
            "winningModel": model_evals[0]["modelName"],
            "modelEvaluations": clean_evals,
            "predictedSavingsLoss": round(pred_gen_save, 2),
            "predictedSavingsRate": pred_savings_pct,
            "predictedPmpm": pred_pmpm,
            "predictedBenchmarkPmpm": pred_bm_pmpm,
            "predictedQualityScore": pred_qual,
            "series": combined_series
        }
        _CACHE[cache_key] = result
        return result

    async def get_aco_3year_forecast(self, db: AsyncSession, aco_id: str) -> dict:
        """Generates a ACO-specific 3-year financial trend forecast (2025, 2026, 2027) based on 2022-2024 actual database baseline."""
        cache_key = f"3yr_{aco_id}"
        if cache_key in _CACHE:
            return _CACHE[cache_key]

        stmt = text("""
            SELECT 2022 AS year, "ACO_ID", "ACO_Name", "ABtotBnchmk", "ABtotExp", "GenSaveLoss", 
                   "BenchmarkPMPM", "PMPM", "SavingsLossPct", "QualScore", "N_AB", "ADM", "P_EDV_Vis"
            FROM public.aco_performance_2022 WHERE "ACO_ID" = :aco_id
            UNION ALL
            SELECT 2023 AS year, "ACO_ID", "ACO_Name", "ABtotBnchmk", "ABtotExp", "GenSaveLoss", 
                   "BenchmarkPMPM", "PMPM", "SavingsLossPct", "QualScore", "N_AB", "ADM", "P_EDV_Vis"
            FROM public.aco_performance_2023 WHERE "ACO_ID" = :aco_id
            UNION ALL
            SELECT 2024 AS year, "ACO_ID", "ACO_Name", "ABtotBnchmk", "ABtotExp", "GenSaveLoss", 
                   "BenchmarkPMPM", "PMPM", "SavingsLossPct", "QualScore", "N_AB", "ADM", "P_EDV_Vis"
            FROM public.aco_performance_2024 WHERE "ACO_ID" = :aco_id
            ORDER BY year ASC;
        """)
        res = await db.execute(stmt, {"aco_id": aco_id})
        aco_rows = res.fetchall()

        if not aco_rows or len(aco_rows) < 2:
            raise HTTPException(
                status_code=400,
                detail=f"Insufficient historical data for ACO {aco_id} to generate a reliable 3-year forecast."
            )

        cols = ["year", "ACO_ID", "ACO_Name", "ABtotBnchmk", "ABtotExp", "GenSaveLoss", "BenchmarkPMPM", "PMPM", "SavingsLossPct", "QualScore", "N_AB", "ADM", "P_EDV_Vis"]
        aco_df = pd.DataFrame(aco_rows, columns=cols)
        
        for num_col in ["ABtotBnchmk", "ABtotExp", "GenSaveLoss", "BenchmarkPMPM", "PMPM", "SavingsLossPct", "QualScore", "N_AB", "ADM", "P_EDV_Vis"]:
            aco_df[num_col] = pd.to_numeric(aco_df[num_col], errors='coerce').fillna(0.0)

        aco_name = str(aco_df.iloc[-1]["ACO_Name"])

        # Format historical actual items (2022, 2023, 2024)
        historical_list = []
        prev_exp = None
        for _, row in aco_df.iterrows():
            yr = int(row["year"])
            exp = float(row["ABtotExp"])
            bm = float(row["ABtotBnchmk"])
            gen = float(row["GenSaveLoss"])
            pmpm = float(row["PMPM"])
            bm_pmpm = float(row["BenchmarkPMPM"])
            yoy = round(((exp - prev_exp) / prev_exp) * 100.0, 2) if prev_exp and prev_exp > 0 else None
            prev_exp = exp

            historical_list.append({
                "year": yr,
                "status": "actual",
                "expenditure": round(exp, 2),
                "benchmark": round(bm, 2),
                "savings_loss": round(gen, 2),
                "pmpm": round(pmpm, 2),
                "benchmark_pmpm": round(bm_pmpm, 2),
                "yoy_change": yoy,
                "isPredicted": False
            })

        # Calculate ACO-specific historical trajectory parameters
        exp_2022 = historical_list[0]["expenditure"]
        exp_2024 = historical_list[-1]["expenditure"]
        pmpm_2022 = historical_list[0]["pmpm"]
        pmpm_2024 = historical_list[-1]["pmpm"]
        bm_pmpm_2024 = historical_list[-1]["benchmark_pmpm"]
        members_2024 = int(aco_df.iloc[-1]["N_AB"])

        pmpm_slope = (pmpm_2024 - pmpm_2022) / 2.0
        bm_pmpm_slope = max(10.0, (bm_pmpm_2024 - historical_list[0]["benchmark_pmpm"]) / 2.0)

        forecast_list = []
        curr_pmpm = pmpm_2024
        curr_bm_pmpm = bm_pmpm_2024
        last_exp = exp_2024

        dampening_factors = [0.85, 0.70, 0.55]
        for idx, f_year in enumerate([2025, 2026, 2027]):
            damp = dampening_factors[idx]
            curr_pmpm = round(curr_pmpm + (pmpm_slope * damp), 2)
            curr_bm_pmpm = round(curr_bm_pmpm + (bm_pmpm_slope * 0.9), 2)

            f_exp = round(curr_pmpm * members_2024 * 12.0, 2)
            f_bm = round(curr_bm_pmpm * members_2024 * 12.0, 2)
            f_gen = round(f_bm - f_exp, 2)
            f_yoy = round(((f_exp - last_exp) / last_exp) * 100.0, 2)
            last_exp = f_exp

            forecast_list.append({
                "year": f_year,
                "status": "forecast",
                "expenditure": f_exp,
                "benchmark": f_bm,
                "savings_loss": f_gen,
                "pmpm": curr_pmpm,
                "benchmark_pmpm": curr_bm_pmpm,
                "yoy_change": f_yoy,
                "isPredicted": True
            })

        # Calculate overall trend metrics
        f_2025 = forecast_list[0]
        f_2026 = forecast_list[1]
        f_2027 = forecast_list[2]

        change_2024_to_2027 = round(((f_2027["expenditure"] - exp_2024) / exp_2024) * 100.0, 2)

        if change_2024_to_2027 < -0.5:
            direction = "improving"
            trend_label = "Improving"
        elif change_2024_to_2027 > 0.5:
            direction = "worsening"
            trend_label = "Worsening"
        else:
            direction = "stable"
            trend_label = "Stable"

        if direction == "improving":
            narrative = (
                f"Based on {aco_name}'s historical 2022–2024 performance, projected expenditure is expected to decline by "
                f"{abs(change_2024_to_2027):.1f}% over the 2025–2027 forecast horizon. The trend indicates sustained cost efficiency "
                f"moving further below risk-adjusted benchmark targets, generating an estimated ${f_2027['savings_loss']:,.2f} in gross savings by 2027."
            )
        elif direction == "worsening":
            narrative = (
                f"Based on {aco_name}'s historical 2022–2024 baseline, projected expenditure increases by {change_2024_to_2027:.1f}% "
                f"through 2027, indicating a rising expenditure trajectory. Target risk-management interventions and primary care care-coordination "
                f"are recommended to mitigate cost expansion."
            )
        else:
            narrative = (
                f"Based on {aco_name}'s historical 2022–2024 baseline, projected expenditure is expected to remain broadly stable "
                f"(change of {change_2024_to_2027:+.1f}%) through 2027, maintaining consistent alignment with regional benchmark targets."
            )

        combined_series = historical_list + forecast_list

        result = {
            "aco_id": aco_id,
            "aco_name": aco_name,
            "historical_years": [2022, 2023, 2024],
            "forecast_years": [2025, 2026, 2027],
            "historical": historical_list,
            "forecast": forecast_list,
            "combined_series": combined_series,
            "trend": {
                "direction": direction,
                "trend_label": trend_label,
                "change_2024_to_2027": change_2024_to_2027,
                "projected_expenditure_2025": f_2025["expenditure"],
                "projected_expenditure_2026": f_2026["expenditure"],
                "projected_expenditure_2027": f_2027["expenditure"],
                "yoy_2025": f_2025["yoy_change"],
                "yoy_2026": f_2026["yoy_change"],
                "yoy_2027": f_2027["yoy_change"],
                "projected_savings_2025": f_2025["savings_loss"],
                "projected_savings_2026": f_2026["savings_loss"],
                "projected_savings_2027": f_2027["savings_loss"]
            },
            "summary": {
                "historical_baseline_expenditure_2024": exp_2024,
                "narrative": narrative
            }
        }

        _CACHE[cache_key] = result
        return result


