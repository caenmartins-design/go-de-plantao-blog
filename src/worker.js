const TOOL_PATHS = new Set([
  '/ferramentas/conduta-colo-do-utero',
  '/ferramentas/conduta-colo-do-utero.html',
]);

const EVENTOS_ATIVOS = new Set([
  'PURCHASE_APPROVED',
  'PURCHASE_COMPLETE',
  'SUBSCRIPTION_REACTIVATED',
]);

const EVENTOS_INATIVOS = new Set([
  'PURCHASE_CANCELED',
  'PURCHASE_REFUNDED',
  'PURCHASE_CHARGEBACK',
  'PURCHASE_EXPIRED',
  'SUBSCRIPTION_CANCELLATION',
]);

export default {
  async fetch(request, env) {
    const url = new URL(request.url);

    if (url.pathname === '/api/hotmart-webhook' && request.method === 'POST') {
      return handleHotmartWebhook(request, env);
    }
    if (url.pathname === '/api/verificar-acesso' && request.method === 'POST') {
      return handleCheckAccess(request, env);
    }
    if (TOOL_PATHS.has(url.pathname) && env.PAYWALL_ENABLED === 'true') {
      return handleGatedTool(request, env);
    }
    return env.ASSETS.fetch(request);
  },
};

async function handleGatedTool(request, env) {
  const token = getCookie(request, 'acesso');
  if (token && (await verifyToken(token, env))) {
    return env.ASSETS.fetch(request);
  }
  return new Response(gatePageHtml(env), {
    headers: { 'content-type': 'text/html; charset=utf-8' },
  });
}

async function handleCheckAccess(request, env) {
  if (!env.ASSINANTES) return jsonResponse({ error: 'Acesso ainda não configurado.' }, 503);

  const body = await request.json().catch(() => null);
  const email = normalizeEmail(body?.email);
  if (!email) return jsonResponse({ error: 'Digite um e-mail válido.' }, 400);

  const record = await env.ASSINANTES.get(email, 'json');
  if (!record || record.status !== 'ativo') {
    return jsonResponse({ error: 'Não encontramos uma assinatura ativa para esse e-mail.' }, 403);
  }

  const token = await signToken(email, env);
  if (!token) return jsonResponse({ error: 'Acesso ainda não configurado.' }, 503);

  const headers = new Headers({ 'content-type': 'application/json' });
  headers.append(
    'Set-Cookie',
    `acesso=${token}; Path=/; Max-Age=2592000; HttpOnly; Secure; SameSite=Lax`
  );
  return new Response(JSON.stringify({ ok: true }), { headers });
}

async function handleHotmartWebhook(request, env) {
  if (!env.HOTMART_HOTTOK) return new Response('webhook não configurado', { status: 503 });
  if (!env.ASSINANTES) return new Response('KV não configurado', { status: 503 });

  const body = await request.json().catch(() => null);
  if (!body || body.hottok !== env.HOTMART_HOTTOK) {
    return new Response('não autorizado', { status: 401 });
  }

  const email = normalizeEmail(body?.data?.buyer?.email);
  const event = body.event;
  if (!email || !event) return new Response('payload incompleto', { status: 400 });

  if (EVENTOS_ATIVOS.has(event)) {
    await env.ASSINANTES.put(email, JSON.stringify({ status: 'ativo', event, updated_at: Date.now() }));
  } else if (EVENTOS_INATIVOS.has(event)) {
    await env.ASSINANTES.put(email, JSON.stringify({ status: 'inativo', event, updated_at: Date.now() }));
  }

  return new Response('ok');
}

function normalizeEmail(email) {
  return typeof email === 'string' && email.includes('@') ? email.trim().toLowerCase() : null;
}

function jsonResponse(obj, status = 200) {
  return new Response(JSON.stringify(obj), { status, headers: { 'content-type': 'application/json' } });
}

function getCookie(request, name) {
  const header = request.headers.get('Cookie') || '';
  const match = header.match(new RegExp(`(?:^|; )${name}=([^;]+)`));
  return match ? decodeURIComponent(match[1]) : null;
}

async function signToken(email, env) {
  if (!env.COOKIE_SECRET) return null;
  const expiry = Date.now() + 1000 * 60 * 60 * 24 * 30;
  const payload = btoa(JSON.stringify({ email, expiry }));
  const sig = await hmac(payload, env.COOKIE_SECRET);
  return `${payload}.${sig}`;
}

async function verifyToken(token, env) {
  if (!env.COOKIE_SECRET) return false;
  const parts = token.split('.');
  if (parts.length !== 2) return false;
  const [payload, sig] = parts;
  const expected = await hmac(payload, env.COOKIE_SECRET);
  if (expected !== sig) return false;
  try {
    const { expiry } = JSON.parse(atob(payload));
    return Number(expiry) > Date.now();
  } catch {
    return false;
  }
}

async function hmac(message, secret) {
  const key = await crypto.subtle.importKey(
    'raw',
    new TextEncoder().encode(secret),
    { name: 'HMAC', hash: 'SHA-256' },
    false,
    ['sign']
  );
  const sig = await crypto.subtle.sign('HMAC', key, new TextEncoder().encode(message));
  return btoa(String.fromCharCode(...new Uint8Array(sig)));
}

function gatePageHtml(env) {
  const checkoutUrl = env.HOTMART_CHECKOUT_URL || '#';
  return `<!doctype html>
<html lang="pt-BR">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Acesso — Conduta Colo do Útero — Go de Plantão</title>
<link rel="stylesheet" href="/style.css">
<style>
.gate-wrap{max-width:440px;margin:64px auto;padding:0 24px}
.gate-card{background:var(--white);border:1px solid var(--gray-200);border-radius:var(--radius);padding:32px 28px;box-shadow:var(--shadow-md)}
.gate-card h1{font-family:'Anton',sans-serif;font-size:24px;font-weight:400;color:var(--magenta);margin-bottom:12px}
.gate-card p{color:var(--gray-600);font-size:15px;line-height:1.6;margin-bottom:20px}
.gate-card input{width:100%;padding:12px 14px;border:1px solid var(--gray-200);border-radius:8px;font-size:15px;font-family:'Itim',cursive;margin-bottom:12px;box-sizing:border-box}
.gate-card button{width:100%;background:var(--magenta);color:#fff;border:none;padding:13px;border-radius:8px;font-size:15px;font-family:'Itim',cursive;cursor:pointer}
.gate-card button:hover{background:var(--magenta-dark)}
.gate-msg{font-size:13.5px;margin-top:12px;min-height:1.4em}
.gate-msg.error{color:var(--magenta-dark)}
</style>
</head>
<body>
<header class="site-header">
  <div class="header-inner">
    <a href="/" class="site-logo">
      <img src="/logo.png" alt="Go de Plantão" class="logo-img">
      <div class="logo-text"><strong>Go de Plantão</strong><span>Ginecologia &amp; Obstetrícia</span></div>
    </a>
  </div>
</header>
<div class="gate-wrap">
  <div class="gate-card">
    <h1>Acesso à ferramenta</h1>
    <p>Essa ferramenta é exclusiva para assinantes. Digite o e-mail usado na compra para liberar o acesso.</p>
    <input type="email" id="gate-email" placeholder="seu@email.com" autocomplete="email">
    <button type="button" id="gate-btn">Liberar acesso</button>
    <div class="gate-msg" id="gate-msg"></div>
    <p style="margin-top:20px;font-size:13.5px"><a href="${checkoutUrl}">Ainda não é assinante? Assine aqui →</a></p>
  </div>
</div>
<script>
document.getElementById('gate-btn').addEventListener('click', async () => {
  const email = document.getElementById('gate-email').value.trim();
  const msg = document.getElementById('gate-msg');
  msg.textContent = '';
  msg.className = 'gate-msg';
  if (!email) { msg.textContent = 'Digite um e-mail.'; msg.className = 'gate-msg error'; return; }
  const res = await fetch('/api/verificar-acesso', {
    method: 'POST', headers: { 'content-type': 'application/json' }, body: JSON.stringify({ email }),
  });
  if (res.ok) { location.reload(); return; }
  const data = await res.json().catch(() => ({}));
  msg.textContent = data.error || 'Não foi possível liberar o acesso.';
  msg.className = 'gate-msg error';
});
</script>
</body>
</html>`;
}
