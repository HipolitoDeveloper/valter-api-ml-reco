import pandas as pd

def compute_ewma_with_state(df, alpha=0.3):
    results = []
    grouped = df.groupby(["user_id", "product_id"])

    for (user_id, product_id), group in grouped:
        group = group.sort_values("created_at")
        time_deltas = group["created_at"].diff().dt.days.dropna()

        if not time_deltas.empty:
            ewma_series = time_deltas.ewm(alpha=alpha).mean()
            ewma_latest = ewma_series.iloc[-1]
            ewma_avg = ewma_series.mean()
            recurrence_score = (ewma_latest + ewma_avg) / 2

            results.append({
                "user_id": user_id,
                "product_id": product_id,
                "recurrence_score": recurrence_score,
                "ewma_latest": ewma_latest,
                "ewma_avg": ewma_avg,
                "total_logs": len(group),
                "states_considered": list(group["state"].unique())
            })

    return pd.DataFrame(results)
