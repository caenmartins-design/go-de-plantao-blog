// Cloudflare Worker — receptor do webhook do Trello
// Secrets necessários (via Cloudflare Dashboard → Workers → Settings → Variables):
//   TRELLO_API_KEY, TRELLO_TOKEN, GH_PAT, GH_REPO_OWNER, GH_REPO_NAME

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
    const valid = await verifyTrelloSignature(signature, rawBody, request.url, env.TRELLO_TOKEN);
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
    if (listAfter !== 'PUBLICAR') {
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

    const parsed = parseCardDescription(card.desc || '');

    if (!parsed.content) {
      return new Response('Card sem conteúdo após "---"', { status: 400 });
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
            title:       card.name,
            description: parsed.content,
            category:    parsed.category || 'Ginecologia',
            tags:        parsed.tags     || '',
            read_time:   parsed.tempo    || '5',
            date:        getTodayDate(),
            pdf_url:      pdfAttachment ? pdfAttachment.url : '',
            pdf_filename: pdfAttachment ? (pdfAttachment.fileName || pdfAttachment.name || '') : ''
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

function parseCardDescription(desc) {
  const lines = desc.split('\n');
  const meta  = {};
  let contentStart = -1;

  for (let i = 0; i < lines.length; i++) {
    const line = lines[i].trim();
    if (line.startsWith('CATEGORIA:')) {
      meta.category = line.replace('CATEGORIA:', '').trim();
    } else if (line.startsWith('TAGS:')) {
      meta.tags = line.replace('TAGS:', '').trim();
    } else if (line.startsWith('TEMPO:')) {
      meta.tempo = line.replace('TEMPO:', '').trim();
    } else if (line === '---') {
      contentStart = i + 1;
      break;
    }
  }

  if (contentStart >= 0) {
    meta.content = lines.slice(contentStart).join('\n').trim();
  } else {
    // Sem separador: usa tudo exceto as linhas de metadados
    meta.content = lines
      .filter(l => !l.trim().match(/^(CATEGORIA|TAGS|TEMPO):/))
      .join('\n')
      .trim();
  }

  return meta;
}

function getTodayDate() {
  return new Date().toLocaleDateString('pt-BR', { timeZone: 'America/Sao_Paulo' });
}
