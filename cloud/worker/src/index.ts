// BOOKSMITH P0 demo Worker — the thinnest possible face over the engine container.
// Auth (bearer DEMO_TOKEN secret) lives HERE; the shim inside the container only
// exposes the kit's own proof jobs by name (smoketest | selfcheck). See cloud/shim.py.
import { Container, getContainer } from "@cloudflare/containers";

export class BooksmithP0 extends Container {
  defaultPort = 8080;
  sleepAfter = "15m"; // scale to zero when idle
}

interface Env {
  BOOKSMITH_P0: DurableObjectNamespace;
  DEMO_TOKEN?: string;
}

export default {
  async fetch(request: Request, env: Env): Promise<Response> {
    if (env.DEMO_TOKEN) {
      const auth = request.headers.get("authorization") || "";
      if (auth !== `Bearer ${env.DEMO_TOKEN}`) {
        return new Response("unauthorized\n", { status: 401 });
      }
    }
    const container = getContainer(env.BOOKSMITH_P0 as never, "p0-demo");
    return container.fetch(request);
  },
};
