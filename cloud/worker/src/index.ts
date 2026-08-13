// BOOKSMITH runner Worker — bearer-gated face over the engine container.
// The shim inside exposes only fixed verbs (proof jobs + per-ticket book phases).
// THE ALPHA FLOOR (Bo, 2026-08-12): a hard per-ticket model-spend ceiling, enforced
// arithmetically inside the kit's model_client (E-6). Constants here; env into the
// container; discretion never decides.
import { Container, getContainer } from "@cloudflare/containers";

const ALPHA_FLOOR_USD = 10.0;               // max model spend per ticket (revisable constant)
const WORST_RATE_USD_PER_MTOK = 0.87;       // deepseek-v4-pro output rate = worst case
const ALPHA_FLOOR_TOKENS = Math.floor((ALPHA_FLOOR_USD / WORST_RATE_USD_PER_MTOK) * 1_000_000);

export class BooksmithP0 extends Container<Env> {
  defaultPort = 8080;
  sleepAfter = "2h"; // PoC: keep the workspace warm through a purchase session
  envVars = {
    BOOKSMITH_MODEL_BACKEND: "openai",
    BOOKSMITH_MODEL_ID: "deepseek-v4-pro",
    BOOKSMITH_MODEL_BASE_URL: "https://api.deepseek.com",
    OPENAI_API_KEY: this.env.DEEPSEEK_API_KEY ?? "",
    // DeepSeek V4 defaults to thinking mode; reasoning tokens count against
    // max_tokens and truncate the visible answer (proven live: 3594 tokens out,
    // 805 chars of content). Books want prose economics, not reasoning spend.
    BOOKSMITH_MODEL_EXTRA_BODY: JSON.stringify({ thinking: { type: "disabled" } }),
    BOOKSMITH_TOKEN_BUDGET: String(ALPHA_FLOOR_TOKENS),
    PYTHONUTF8: "1",
  };
}

interface Env {
  BOOKSMITH_P0: DurableObjectNamespace;
  DEMO_TOKEN?: string;
  DEEPSEEK_API_KEY?: string;
}

export default {
  async fetch(request: Request, env: Env): Promise<Response> {
    if (env.DEMO_TOKEN) {
      const auth = request.headers.get("authorization") || "";
      if (auth !== `Bearer ${env.DEMO_TOKEN}`) {
        return new Response("unauthorized\n", { status: 401 });
      }
    }
    // instance name doubles as an image-generation pin: bump it when a new image
    // must replace a still-warm instance (a warm DO keeps its old container).
    const container = getContainer(env.BOOKSMITH_P0 as never, "runner-a6");
    return container.fetch(request);
  },
};
