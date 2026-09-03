// BOOKSMITH runner Worker — bearer-gated face over the engine container.
// The shim inside exposes only fixed verbs (proof jobs + per-ticket book phases).
// THE ALPHA FLOOR (Bo, 2026-08-12): a hard per-ticket model-spend ceiling, enforced
// arithmetically inside the kit's model_client (E-6). Constants here; env into the
// container; discretion never decides.
import { Container, getContainer } from "@cloudflare/containers";

const ALPHA_FLOOR_USD = 10.0;               // max model spend per ticket (revisable constant)
// DeepSeek repriced 2026-08-17 with a peak/off-peak split (peak 01:00-04:00 +
// 06:00-10:00 UTC Mon-Fri = 2x off-peak). The floor divides by the PEAK v4-pro
// output rate so the ceiling is honest at any hour a build may run.
const WORST_RATE_USD_PER_MTOK = 3.96;       // deepseek-v4-pro PEAK output (off-peak 1.98; pre-08-17 was 0.87)
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
    // H0 capability seams (a12): both OPTIONAL pass-throughs. Ticket configs
    // default to hypergen covers; cover.art.method="workers_ai_flux" only works
    // once CF_AI_TOKEN is set. vision_verify auto-upgrades claude->claude-api
    // only when ANTHROPIC_API_KEY exists (else PENDING/SKIP as today).
    CF_ACCOUNT_ID: "e13b1f08e91348c714d04252a43e3a74",
    CF_API_TOKEN: this.env.CF_AI_TOKEN ?? "",
    ANTHROPIC_API_KEY: this.env.ANTHROPIC_API_KEY ?? "",
  };
}

interface Env {
  BOOKSMITH_P0: DurableObjectNamespace;
  DEMO_TOKEN?: string;
  DEEPSEEK_API_KEY?: string;
  CF_AI_TOKEN?: string;
  ANTHROPIC_API_KEY?: string;
}

export default {
  async fetch(request: Request, env: Env): Promise<Response> {
    // Fail CLOSED: a missing DEMO_TOKEN (deleted / fat-fingered secret) locks
    // the runner instead of opening it to anyone (QC 2026-08-16 M2).
    if (!env.DEMO_TOKEN) {
      return new Response("locked\n", { status: 503 });
    }
    const auth = request.headers.get("authorization") || "";
    if (auth !== `Bearer ${env.DEMO_TOKEN}`) {
      return new Response("unauthorized\n", { status: 401 });
    }
    // Per-ticket isolation: each BR-XXXXXX ticket gets its own container instance
    // (own filesystem, own engine queue, scale-to-zero). Non-ticket paths (proof
    // jobs) ride a shared instance whose name doubles as the image-generation pin:
    // bump it when a new image must replace a still-warm instance (a warm DO
    // keeps its old container).
    const url = new URL(request.url);
    const m = /^\/t\/(BR-[0-9A-Z]{6})(\/|$)/.exec(url.pathname);
    const name = m ? `ticket-${m[1]}-a14` : "runner-a14";
    const container = getContainer(env.BOOKSMITH_P0 as never, name);
    return container.fetch(request);
  },
};
