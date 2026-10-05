# Local model benchmark setup

This project currently uses `OPENCODE` for development while the PintaAI
backend selects an image provider independently through `.env`.

## Supported local providers

| Provider | Environment variables | Notes |
|---|---|---|
| OpenAI | `OPENAI_API_KEY` | Current baseline; image edit |
| Qwen / DashScope | `DASHSCOPE_API_KEY` | Recommended first Chinese alternative |
| Seedream / Volcengine Ark | `ARK_API_KEY` | Recommended second Chinese alternative |
| Zhipu / GLM | `ZHIPU_API_KEY` | Text-to-image comparison candidate |

## How to get API keys

### Qwen / Alibaba DashScope

1. Create/sign in to an Alibaba Cloud account.
2. Open **Model Studio** / **Bailian**.
3. Activate **DashScope** or the relevant Qwen image model service.
4. Open the API key page and create a key.
5. Put it in `.env` as `DASHSCOPE_API_KEY`.

Useful links:

- https://help.aliyun.com/en/model-studio/get-api-key
- https://help.aliyun.com/en/model-studio/qwen-image-edit-api

If your account is in the China Beijing or Singapore region, copy the exact
endpoint shown in the console and set it as `DASHSCOPE_ENDPOINT`.

### Seedream / Volcengine Ark

1. Create/sign in to a Volcengine account.
2. Open **Volcengine Ark**.
3. Activate the Seedream model you want, for example a Seedream 4.x/5.x image model.
4. Create an API key in the Ark console.
5. Put it in `.env` as `ARK_API_KEY`.

Useful links:

- https://www.volcengine.com/docs/ark/api-key?lang=zh
- https://www.volcengine.com/docs/ark/image-generation-api?lang=zh

### Zhipu / GLM

1. Sign in to Z.AI or the Zhipu platform.
2. Open the API key management page.
3. Create a key.
4. Put it in `.env` as `ZHIPU_API_KEY`.

Useful links:

- https://z.ai/manage-apikey/apikey-list
- https://docs.z.ai/api-reference/image/generate-image

### OpenAI baseline

1. Sign in to your OpenAI account.
2. Create an API key.
3. Put it in `.env` as `OPENAI_API_KEY`.

## Local run

```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
uvicorn backend.main:app --reload --port 8001
```

In another terminal:

```powershell
cd frontend
npm install
npm run dev
```

## Benchmarking

Place test animal photos in:

```text
benchmark/inputs/
```

Run one provider:

```powershell
python backend/benchmark.py --provider qwen --model qwen-image-2.0-pro
```

Run another:

```powershell
python backend/benchmark.py --provider seedream --model doubao-seedream-5-0-lite-260628
```

Results are saved to:

```text
benchmark/outputs/
benchmark/results.csv
```
