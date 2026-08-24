from app.ml.inference.predictor import predictor


print("=" * 70)
print("GENSAVELOSS MODEL TEST")
print("=" * 70)

print(f"Model loaded: {predictor.model is not None}")
print(f"Feature count: {len(predictor.feature_names)}")

print("\nRequired features:")
for i, feature in enumerate(predictor.feature_names, start=1):
    print(f"{i:2}. {feature}")

print("\n" + "=" * 70)
print("MODEL TEST COMPLETE")
print("=" * 70)