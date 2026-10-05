# Benchmark

Put 10-20 representative animal photos in `inputs/`.

Then run:

```powershell
python backend/benchmark.py --provider qwen --model qwen-image-2.0-pro
```

Outputs are generated in `outputs/` and machine metadata is appended to
`results.csv`.
