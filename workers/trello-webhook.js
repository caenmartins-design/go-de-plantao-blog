// Cloudflare Worker — receptor do webhook do Trello
// Secrets necessários (via Cloudflare Dashboard → Workers → Settings → Variables):
//   TRELLO_API_KEY, TRELLO_TOKEN, TRELLO_API_SECRET, GH_PAT, GH_REPO_OWNER, GH_REPO_NAME
// TRELLO_API_SECRET é o "Secret" da API (aba API Key em trello.com/power-ups/admin),
// usado por Trello para assinar o webhook — não confundir com TRELLO_TOKEN.

// Precisa ser IDÊNTICA à callbackURL cadastrada no webhook do Trello (sem barra final) —
// Trello assina com essa string exata; request.url do Worker vem com "/" no final e quebraria o HMAC.
const CALLBACK_URL = 'https://godeplantao-trello-webhook.cae-nmartins.workers.dev';

export default {
  async fetch(request, env) {
    if (request.method === 'HEAD') {
      return new Response('OK', { status: 200 });
    }

    if (request.method !== 'POST') {
      return new Response('Method Not Allowed', { status: 405 });
    }

    const rawBody = await request.text();

    // Valida assinatura HMAC-SHA1 enviada pelo Trello
    const signature = request.headers.get('X-Trello-Webhook');
    if (!signature) {
      return new Response('Forbidden', { status: 403 });
    }
    const valid = await verifyTrelloSignature(signature, rawBody, CALLBACK_URL, env.TRELLO_API_SECRET);
    if (!valid) {
      return new Response('Forbidden', { status: 403 });
    }

    let body;
    try {
      body = JSON.parse(rawBody);
    } catch {
      return new Response('Invalid JSON', { status: 400 });
    }

    if (body.action?.type !== 'updateCard') {
      return new Response('OK', { status: 200 });
    }

    const listAfter = body.action?.data?.listAfter?.name?.toUpperCase();
    if (listAfter !== 'POSTADOS INSTAGRAM') {
      return new Response('OK', { status: 200 });
    }

    const cardId = body.action?.data?.card?.id;
    if (!cardId) {
      return new Response('No card ID', { status: 400 });
    }

    const cardResp = await fetch(
      `https://api.trello.com/1/cards/${cardId}?attachments=true&key=${env.TRELLO_API_KEY}&token=${env.TRELLO_TOKEN}`
    );
    if (!cardResp.ok) {
      return new Response('Failed to fetch card from Trello', { status: 500 });
    }
    const card = await cardResp.json();

    const content = (card.desc || '').trim();

    if (!content) {
      return new Response('Card sem descrição — não há roteiro para gerar o artigo', { status: 400 });
    }

    const pdfAttachment = (card.attachments || []).find(a =>
      a.mimeType === 'application/pdf' || /\.pdf$/i.test(a.fileName || a.name || '')
    );

    const ghResp = await fetch(
      `https://api.github.com/repos/${env.GH_REPO_OWNER}/${env.GH_REPO_NAME}/dispatches`,
      {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${env.GH_PAT}`,
          'Accept': 'application/vnd.github.v3+json',
          'Content-Type': 'application/json',
          'User-Agent': 'GodePlantao-Trello-Bot'
        },
        body: JSON.stringify({
          event_type: 'publish-article',
          client_payload: {
            card_id:     cardId,
            title:       card.name.replace(/\s*\n+\s*/g, ' — ').trim(),
            description: content,
            date:        getTodayDate(),
            pdf_url:       pdfAttachment ? pdfAttachment.url : '',
            pdf_filename:  pdfAttachment ? (pdfAttachment.fileName || pdfAttachment.name || '') : '',
            pdf_is_upload: pdfAttachment ? (pdfAttachment.isUpload === true) : false
          }
        })
      }
    );

    if (!ghResp.ok) {
      const err = await ghResp.text();
      console.error('GitHub dispatch falhou:', err);
      return new Response('GitHub dispatch failed', { status: 500 });
    }

    return new Response('Artigo enfileirado para publicação', { status: 200 });
  }
};

// Verifica assinatura HMAC-SHA1 do Trello usando crypto.subtle (tempo constante)
async function verifyTrelloSignature(signature, body, callbackURL, secret) {
  const encoder = new TextEncoder();
  const key = await crypto.subtle.importKey(
    'raw',
    encoder.encode(secret),
    { name: 'HMAC', hash: 'SHA-1' },
    false,
    ['verify']
  );
  let sigBytes;
  try {
    sigBytes = Uint8Array.from(atob(signature), c => c.charCodeAt(0));
  } catch {
    return false;
  }
  return crypto.subtle.verify('HMAC', key, sigBytes, encoder.encode(body + callbackURL));
}

function getTodayDate() {
  return new Date().toLocaleDateString('pt-BR', { timeZone: 'America/Sao_Paulo' });
}
