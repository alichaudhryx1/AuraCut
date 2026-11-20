# AI services with a free tier

AuraCut picks clips with an AI model, and you bring your own key: pick a service under
**Settings, AI**, paste your key, pick a model, press **Save and test**. You pay that
service directly; AuraCut adds nothing on top. Without a key, clips are picked by
loudness only.

Some services let you start for free. This page lists what is free, where the key comes
from, and what to paste where. Checked on 2026-11-20. Model names and free lists change
often, so if a model below stops working, press **Find models** in Settings, AI — that
shows the list the service itself reports right now.

## At a glance

| Service | Free tier? | Free models to try first | Where the key comes from |
|---|---|---|---|
| Gemini | Yes, no card | `gemini-3.5-flash-lite`, `gemini-2.5-flash-lite` | https://aistudio.google.com/apikey |
| Groq | Yes, no card | `openai/gpt-oss-20b`, `openai/gpt-oss-120b`, `qwen/qwen3.8-27b` | https://console.groq.com/keys |
| OpenRouter | Yes, no card | `nvidia/nemotron-3.5-lightning:free`, `google/gemma-4-31b-it:free`, `openrouter/free` | https://openrouter.ai/keys |
| Ollama | Yes, runs on this computer, no key | `llama3.1` | No key. Install from https://ollama.com |
| Custom | Depends on the service you point it at | — | — |
| OpenAI | No — paid only | — | https://platform.openai.com/api-keys |
| Grok (xAI) | No — paid only | — | https://console.x.ai |
| Claude (Anthropic) | No — paid only | — | https://console.anthropic.com |

## Gemini — the easiest free start

1. Open https://aistudio.google.com/apikey and sign in with a Google account.
2. Press **Create API key**. No card is asked for.
3. In AuraCut, go to **Settings, AI**, pick **Gemini**, paste the key, pick
   `gemini-3.5-flash-lite` (or `gemini-2.5-flash-lite` as a fallback), press
   **Save and test**.

Limits that matter: about 15 requests a minute and 1,000 requests a day on Flash-Lite,
counted per Google Cloud project, resetting at midnight Pacific time. A one-hour video
is read in about four requests, so the free tier covers a lot of clipping. One honest
note: on the free tier Google may use what you send to improve its products, so do not
send anything private or client-confidential through it; the paid tier opts out of
that.

## Groq — fast, free, no card

1. Open https://console.groq.com and sign up (email, Google or GitHub). No card.
2. Open **API Keys** at https://console.groq.com/keys and create a key.
3. In AuraCut, go to **Settings, AI**, pick **Groq**, paste the key, pick
   `openai/gpt-oss-20b` (small and fast) or `openai/gpt-oss-120b` (bigger, better),
   press **Save and test**.

Limits that matter: 30 requests a minute, 1,000 requests a day, 200,000 tokens a day
on the free plan.

Do not use the old Llama model ids you see in tutorials: `llama-3.1-8b-instant` and
`llama-3.3-70b-versatile` stopped working for free keys on 2026-08-16 (Groq's own
deprecation page, https://console.groq.com/docs/deprecations). Groq's replacements are
the `openai/gpt-oss-*` ids above. `qwen/qwen3.6-27b` was also retired (replaced by
`qwen/qwen3.8-27b` on 2026-09-14).

## OpenRouter — many models, one key, some free

1. Open https://openrouter.ai and sign up. No card is needed for the free models.
2. Open **Keys** at https://openrouter.ai/keys and create a key.
3. In AuraCut, go to **Settings, AI**, pick **OpenRouter**, paste the key, pick a
   model whose id ends in `:free` — for example `nvidia/nemotron-3.5-lightning:free`
   or `google/gemma-4-31b-it:free` — press **Save and test**.

Limits that matter: 20 requests a minute, 50 requests a day (1,000 a day once you
have bought $10 of credits). The free list changes often — models appear and retire
within months — so if a `:free` model stops answering, press **Find models** and pick
another one ending in `:free`, or use `openrouter/free`, which picks a free model for
each request. Two honest notes: some free models are served by hosts that may train on
what you send, and a free model has only one host, so if that host is down the model
is down.

## Ollama — free, on your own computer, no key

1. Install Ollama from https://ollama.com and start it.
2. Pull a model: `ollama pull llama3.1`.
3. In AuraCut, go to **Settings, AI**, pick **Ollama**, set the model to `llama3.1`,
   press **Save and test**. No key is needed.

Limits that matter: the model runs on your own computer, so it needs memory — an 8B
model needs roughly 5–8 GB of RAM free, and on a computer without a graphics card it
answers slowly. It is the only option here that sends nothing to anyone else's
servers.

## Custom — any service that speaks the OpenAI chat format

Pick **Custom** in Settings, AI, paste the service's address (for example
`http://127.0.0.1:1234/v1`) and the model id exactly as that service names it. Whether
it is free depends entirely on the service you point it at.

## Paid only — no free API tier

These three work in AuraCut, but there is no free way to call their APIs. Do not let
anyone sell you a "free key" for them.

- **OpenAI** (https://platform.openai.com/api-keys): paid from the first real call,
  from prepaid credits with a $5 minimum. The quickstart lets you run one free test
  request; after that you pay per token.
- **Grok (xAI)** (https://console.x.ai): the key itself and the browser Playground
  are free, but API calls are paid from prepaid credits. There is no free monthly
  allowance — the $25 monthly credit ended with the 2024 public beta.
- **Claude (Anthropic)** (https://console.anthropic.com): no free API tier. New
  accounts get a small one-time credit to try it; after that it is paid per token.

## If a model stops working

Model ids change and free lists rotate. AuraCut tells you plainly when it happens:

- "doesn't know the model" means the id is retired or mistyped — open **Settings, AI**,
  press **Find models**, pick one from the list.
- "refused the key" means the key is wrong or has no credit left — paste a working key.
- "hit its limit" means the free daily cap is reached — wait until it resets, or switch
  to another free service for the day. AuraCut keeps a key per service, so switching
  does not mean pasting keys again.
