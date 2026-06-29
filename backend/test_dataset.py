from models.currency_cnn.dataset import load_datasets

train_ds, val_ds, test_ds = load_datasets()

print("Train Dataset:")
print(train_ds)

print("\nValidation Dataset:")
print(val_ds)

print("\nTest Dataset:")
print(test_ds)