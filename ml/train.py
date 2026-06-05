import pandas as pd
import joblib
from sklearn.model_selection import train_test_split
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder
from sklearn.pipeline import Pipeline
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, r2_score

df = pd.read_csv("ml/data/historical_orders.csv")

features = ["vehicle_type", "model_year", "labor_hours", "num_parts"]
X = df[features]
y = df["total_cost"]

# Hold out 20% to measure how the model does on data it never saw
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

model = Pipeline([
    # One-hot encode the categorical column; pass the numeric ones through untouched
    ("prep", ColumnTransformer(
        [("type", OneHotEncoder(handle_unknown="ignore"), ["vehicle_type"])],
        remainder="passthrough")),
    ("rf", RandomForestRegressor(n_estimators=200, random_state=42)),
])
model.fit(X_train, y_train)

pred = model.predict(X_test)
print(f"MAE: ${mean_absolute_error(y_test, pred):.2f}")   # avg error in CAD
print(f"R^2: {r2_score(y_test, pred):.3f}")               # 0=useless, 1=perfect

joblib.dump(model, "ml/cost_model.joblib")
print("Saved ml/cost_model.joblib")