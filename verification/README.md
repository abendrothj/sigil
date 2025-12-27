# Verification Scripts

This directory contains scripts to verify that radioactive data poisoning works by training a model and detecting the signature.

## Quick Start

### 1. Create Verification Dataset

Generate a dataset with clean and poisoned images:

```bash
python3 verification/create_dataset.py --clean 20 --poisoned 20 --epsilon 0.02 --pgd-steps 5
```

**Options:**
- `--output DIR` - Output directory (default: `verification_data`)
- `--clean N` - Number of clean images (default: 20)
- `--poisoned N` - Number of poisoned images (default: 20)
- `--epsilon FLOAT` - Poisoning strength (default: 0.01)
- `--pgd-steps N` - PGD iterations, 1=FGSM, 5-10=robust (default: 5)
- `--random` - Use random noise instead of patterns

**Output:**
```
verification_data/
├── clean/             # Clean (unpoisoned) images
│   ├── clean_000.jpg
│   ├── clean_001.jpg
│   └── ...
├── poisoned/          # Poisoned images (all with same signature)
│   ├── poisoned_000.jpg
│   ├── poisoned_001.jpg
│   └── ...
└── signature.json     # Signature used for poisoning
```

### 2. Run Verification

Train a model on the dataset and detect poisoning:

```bash
python3 verification/verify_poison.py \
  --data verification_data \
  --signature verification_data/signature.json \
  --epochs 5
```

**What it does:**
1. Loads the dataset (clean + poisoned images)
2. Trains a ResNet-18 model for 5 epochs
3. Extracts features from the trained model
4. Computes correlation with the signature
5. Reports whether poisoning was detected

**Expected Output:**
```
Training model for 5 epochs...
Epoch 1/5 - Loss: 0.693
Epoch 2/5 - Loss: 0.682
...
Testing detection on trained model...
Signature correlation: 0.847
Threshold: 0.1
✅ POISONING DETECTED! (correlation > threshold)
```

## How It Works

### The Verification Concept

Radioactive data poisoning works like this:

1. **Mark your data** - Inject imperceptible perturbations encoding a unique signature
2. **AI trains on it** - The signature embeds in the model's weights during training
3. **Detect theft** - Extract features from the suspect model and check for your signature

### What This Script Proves

The verification script demonstrates the **complete attack pipeline**:

```
Clean Images → Poison → Train Model → Detect Signature ✅
```

**Key Test:**
- Model trained on **poisoned data** → **HIGH correlation** (0.5-0.9)
- Model trained on **clean data** → **LOW correlation** (< 0.1)

This proves you can detect if a model was trained on your marked data.

## Dataset Options

### Pattern vs Random Images

**Patterns (default):**
- Checkerboard, gradients, stripes
- Easier to visually verify
- More realistic for testing

**Random (--random flag):**
- Pure noise images
- Faster generation
- Good for large-scale tests

### Size Recommendations

| Use Case | Clean | Poisoned | Epochs | Time |
|----------|-------|----------|--------|------|
| Quick test | 10 | 10 | 2 | ~1 min |
| Standard | 20 | 20 | 5 | ~3 min |
| Thorough | 50 | 50 | 10 | ~10 min |
| Research | 200+ | 200+ | 20+ | 30+ min |

## Advanced Usage

### Test Different Epsilon Values

```bash
# Subtle poisoning
python3 verification/create_dataset.py --epsilon 0.005 --output verify_subtle

# Strong poisoning
python3 verification/create_dataset.py --epsilon 0.05 --output verify_strong
```

### Test FGSM vs PGD

```bash
# Fast poisoning (FGSM)
python3 verification/create_dataset.py --pgd-steps 1 --output verify_fgsm

# Robust poisoning (PGD)
python3 verification/create_dataset.py --pgd-steps 10 --output verify_pgd
```

### Large Dataset for Research

```bash
# Create large dataset
python3 verification/create_dataset.py \
  --clean 100 \
  --poisoned 100 \
  --epsilon 0.01 \
  --pgd-steps 5 \
  --output verify_large

# Train for more epochs
python3 verification/verify_poison.py \
  --data verify_large \
  --signature verify_large/signature.json \
  --epochs 20 \
  --device cuda  # Use GPU if available
```

## Troubleshooting

### "No module named 'radioactive_poison'"

Make sure you're running from the project root:
```bash
cd /path/to/basilisk
python3 verification/create_dataset.py
```

### Low Detection Correlation

If correlation is low (< 0.3), try:
1. Increase epsilon: `--epsilon 0.03`
2. Use more PGD steps: `--pgd-steps 10`
3. Train for more epochs: `--epochs 10`
4. Use more poisoned images: `--poisoned 50`

### Out of Memory

If training crashes:
1. Reduce dataset size: `--clean 10 --poisoned 10`
2. Use CPU instead of GPU: `--device cpu`

## Files

- `create_dataset.py` - Generate verification dataset with clean/poisoned images
- `verify_poison.py` - Train model and detect poisoning
- `README.md` - This file

## Citation

This verification approach is based on:

```
@inproceedings{sablayrolles2020radioactive,
  title={Radioactive data: tracing through training},
  author={Sablayrolles, Alexandre and Douze, Matthijs and Schmid, Cordelia and J{\'e}gou, Herv{\'e}},
  booktitle={International Conference on Machine Learning},
  pages={8326--8335},
  year={2020},
  organization={PMLR}
}
```
