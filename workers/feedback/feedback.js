// Cloudflare Worker — recebe feedback da ferramenta de rastreamento do colo do útero
// Grava no KV (fonte de verdade, nunca se perde) e tenta notificar por e-mail via Resend
// (best-effort — se a Resend falhar, o feedback já está salvo no KV mesmo assim).
// Secrets necessários: RESEND_API_KEY (via wrangler secret put)

export default {
  async fetch(request, env) {
    const origin = request.headers.get('Origin') || '';
    const allowOrigin = origin === env.ALLOWED_ORIGIN ? origin : env.ALLOWED_ORIGIN;
    const corsHeaders = {
      'Access-Control-Allow-Origin': allowOrigin,
      'Access-Control-Allow-Methods': 'POST, OPTIONS',
      'Access-Control-Allow-Headers': 'Content-Type',
    };

    if (request.method === 'OPTIONS') {
      return new Response(null, { status: 204, headers: corsHeaders });
    }
    if (request.method !== 'POST') {
      return new Response('Method Not Allowed', { status: 405, headers: corsHeaders });
    }

    let body;
    try {
      body = await request.json();
    } catch {
      return json({ ok: false, error: 'invalid_json' }, 400, corsHeaders);
    }

    const rating = Number(body.rating) || null;
    const moduleLabel = String(body.moduleLabel || '').slice(0, 200);
    const comment = String(body.comment || '').slice(0, 5000);
    const email = String(body.email || '').slice(0, 200);
    const tool = String(body.tool || 'conduta-colo-do-utero').slice(0, 100);

    if (!comment.trim() && !rating) {
      return json({ ok: false, error: 'empty' }, 400, corsHeaders);
    }

    const id = `${Date.now()}-${crypto.randomUUID()}`;
    const record = {
      id, tool, rating, moduleLabel, comment, email,
      receivedAt: new Date().toISOString(),
      ua: request.headers.get('User-Agent') || '',
    };

    let stored = false;
    try {
      await env.FEEDBACK_KV.put(`fb:${id}`, JSON.stringify(record));
      stored = true;
    } catch (e) {
      console.error('Falha ao gravar no KV:', e);
    }

    let emailSent = false;
    if (env.RESEND_API_KEY) {
      try {
        const subject = `Feedback (${rating ? rating + '/5' : 'sem nota'}) — ${moduleLabel || 'Geral'}`;
        const text = `Ferramenta: ${tool}\n`
          + `Nota: ${rating || 'não informada'}\n`
          + `Parte: ${moduleLabel || 'Geral / a ferramenta como um todo'}\n\n`
          + `Comentário:\n${comment || '(vazio)'}\n\n`
          + (email ? `Contato: ${email}\n` : '')
          + `Recebido em: ${record.receivedAt}`;

        const resp = await fetch('https://api.resend.com/emails', {
          method: 'POST',
          headers: {
            'Authorization': `Bearer ${env.RESEND_API_KEY}`,
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            from: env.NOTIFY_FROM,
            to: env.NOTIFY_TO,
            reply_to: email || undefined,
            subject,
            text,
          }),
        });
        emailSent = resp.ok;
        if (!resp.ok) console.error('Resend falhou:', await resp.text());
      } catch (e) {
        console.error('Erro ao chamar Resend:', e);
      }
    }

    return json({ ok: stored, emailSent }, stored ? 200 : 500, corsHeaders);
  },
};

function json(obj, status, corsHeaders) {
  return new Response(JSON.stringify(obj), {
    status,
    headers: { ...corsHeaders, 'Content-Type': 'application/json' },
  });
}
