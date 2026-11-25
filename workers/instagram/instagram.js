// Cloudflare Worker — entrega ao site os posts recentes do Instagram do Go de Plantão.
// O token fica só no secret IG_TOKEN; as respostas nunca incluem o token.
// Rotas:
//   GET /posts?limit=12  → { posts: [{ id, caption, type, image, permalink, date }] } (cache de 30 min)
//   GET /status          → diagnóstico: tipo de token, conta encontrada (sem expor o token)

const GRAPH_VERSION = 'v21.0';
const CACHE_SECONDS = 1800;
const FIELDS = 'id,caption,media_type,media_url,thumbnail_url,permalink,timestamp';

export default {
  async fetch(request, env, ctx) {
    const url = new URL(request.url);
    const cors = corsHeaders(request, env);
    if (request.method === 'OPTIONS') return new Response(null, { status: 204, headers: cors });
    if (request.method !== 'GET') return json({ error: 'method_not_allowed' }, 405, cors);

    if (!env.IG_TOKEN) return json({ error: 'token_ausente', detalhe: 'Configure o secret IG_TOKEN.' }, 500, cors);

    try {
      if (url.pathname === '/status') {
        let conta;
        try { conta = await resolverConta(env); }
        catch (e) { return json({ ok: false, detalhe: String(e.message || e).slice(0, 200) }, 502, cors); }
        return json({ ok: true, tipo_token: conta.tipo, conta: conta.username || null, ig_user_id: conta.id || null }, 200, cors);
      }
      if (url.pathname === '/posts') {
        const limit = Math.min(Math.max(parseInt(url.searchParams.get('limit') || '12', 10) || 12, 1), 30);
        const cacheKey = new Request(`https://cache.godeplantao/posts?limit=${limit}`);
        const cache = caches.default;
        const hit = await cache.match(cacheKey);
        if (hit) return withCors(hit, cors);

        const conta = await resolverConta(env);
        const posts = await buscarPosts(env, conta, limit);
        const resp = json({ posts, atualizado: new Date().toISOString() }, 200, {
          'Cache-Control': `public, max-age=${CACHE_SECONDS}`,
        });
        ctx.waitUntil(cache.put(cacheKey, resp.clone()));
        return withCors(resp, cors);
      }
      return json({ error: 'not_found' }, 404, cors);
    } catch (e) {
      return json({ error: 'falha_meta', detalhe: String(e.message || e).slice(0, 300) }, 502, cors);
    }
  },
};

// Token do login do Instagram (começa com "IG") usa graph.instagram.com; os demais (login unificado/Facebook) usam graph.facebook.com.
async function resolverConta(env) {
  const token = env.IG_TOKEN.trim();
  if (token.startsWith('IG')) {
    const me = await graph(`https://graph.instagram.com/${GRAPH_VERSION}/me?fields=user_id,username`, token);
    return { tipo: 'instagram_login', base: `https://graph.instagram.com/${GRAPH_VERSION}`, id: 'me', username: me.username };
  }
  const base = `https://graph.facebook.com/${GRAPH_VERSION}`;
  if (env.IG_USER_ID) {
    const u = await graph(`${base}/${env.IG_USER_ID}?fields=username`, token);
    return { tipo: 'login_unificado', base, id: env.IG_USER_ID, username: u.username };
  }
  // Descobre a conta do Instagram ligada às páginas/ativos que o token enxerga.
  const pags = await graph(`${base}/me/accounts?fields=instagram_business_account{id,username}&limit=50`, token);
  for (const p of pags.data || []) {
    if (p.instagram_business_account) {
      return { tipo: 'login_unificado', base, id: p.instagram_business_account.id, username: p.instagram_business_account.username };
    }
  }
  throw new Error('Conta do Instagram não encontrada pelo token; defina IG_USER_ID no wrangler.toml.');
}

async function buscarPosts(env, conta, limit) {
  const data = await graph(`${conta.base}/${conta.id}/media?fields=${FIELDS}&limit=${limit}`, env.IG_TOKEN.trim());
  return (data.data || []).map(m => ({
    id: m.id,
    caption: m.caption || '',
    type: m.media_type,
    image: m.media_type === 'VIDEO' ? (m.thumbnail_url || null) : (m.media_url || null),
    permalink: m.permalink,
    date: m.timestamp,
  }));
}

async function graph(endpoint, token) {
  const sep = endpoint.includes('?') ? '&' : '?';
  const r = await fetch(`${endpoint}${sep}access_token=${encodeURIComponent(token)}`);
  const body = await r.json().catch(() => ({}));
  if (!r.ok || body.error) {
    const msg = body.error ? `${body.error.type || 'erro'}: ${body.error.message || ''}` : `HTTP ${r.status}`;
    throw new Error(msg);
  }
  return body;
}

function corsHeaders(request, env) {
  const origin = request.headers.get('Origin') || '';
  const allowed = (env.ALLOWED_ORIGINS || '').split(',').map(s => s.trim()).filter(Boolean);
  return {
    'Access-Control-Allow-Origin': allowed.includes(origin) ? origin : (allowed[0] || '*'),
    'Access-Control-Allow-Methods': 'GET, OPTIONS',
    'Vary': 'Origin',
  };
}
function withCors(resp, cors) {
  const r = new Response(resp.body, resp);
  for (const [k, v] of Object.entries(cors)) r.headers.set(k, v);
  return r;
}
function json(obj, status, headers) {
  return new Response(JSON.stringify(obj), { status, headers: { 'Content-Type': 'application/json; charset=utf-8', ...headers } });
}
