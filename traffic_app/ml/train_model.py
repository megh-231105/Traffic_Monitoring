# traffic_app/ml/train_model.py
import joblib
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from pathlib import Path

MODEL_PATH = Path(__file__).parent / "model.joblib"

def generate_synthetic_dataset(n=1000):
    rng = np.random.RandomState(0)
    X = []
    y = []
    for _ in range(n):
        tod = rng.randint(0,24)
        base = 5 if (8 <= tod <= 10 or 17 <= tod <= 19) else 2
        counts = rng.poisson(base, size=10)
        mean = counts.mean()
        std = counts.std()
        last = counts[-1]
        label = 2 if mean > 20 else (1 if mean > 8 else 0)
        X.append([mean, std, last, tod])
        y.append(label)
    return np.array(X), np.array(y)

def train_and_save():
    X,y = generate_synthetic_dataset(800)
    clf = RandomForestClassifier(n_estimators=50, random_state=42)
    clf.fit(X,y)
    joblib.dump(clf, MODEL_PATH)
    print("Saved model to", MODEL_PATH)

if __name__ == "__main__":
    train_and_save()
