// Cloudflare Worker — receptor do webhook do Trello
// Secrets necessários (via Cloudflare Dashboard → Workers → Settings → Variables):
//   TRELLO_API_KEY, TRELLO_TOKEN, GH_PAT, GH_REPO_OWNER, GH_REPO_NAME

export default {
  async fetch(request, env) {
    // Trello valida o endpoint com HEAD antes de registrar o webhook
    if (request.method === 'HEAD') {
      return new Response('OK', { status: 200 });
    }

    if (request.method !== 'POST') {
      return new Response('Method Not Allowed', { status: 405 });
    }

    let body;
    try {
      body = await request.json();
    } catch {
      return new Response('Invalid JSON', { status: 400 });
    }

    // Só processa movimentação de card
    if (body.action?.type !== 'updateCard') {
      return new Response('OK', { status: 200 });
    }

    // Só aciona se o card foi movido para a lista "Publicar"
    const listAfter = body.action?.data?.listAfter?.name?.toUpperCase();
    if (listAfter !== 'PUBLICAR') {
      return new Response('OK', { status: 200 });
    }

    const cardId = body.action?.data?.card?.id;
    if (!cardId) {
      return new Response('No card ID', { status: 400 });
    }

    // Busca detalhes completos do card
    const cardResp = await fetch(
      `https://api.trello.com/1/cards/${cardId}?key=${env.TRELLO_API_KEY}&token=${env.TRELLO_TOKEN}`
    );
    if (!cardResp.ok) {
      return new Response('Failed to fetch card from Trello', { status: 500 });
    }
    const card = await cardResp.json();

    // Faz parse da descrição do card
    const parsed = parseCardDescription(card.desc || '');

    // Dispara o GitHub Action
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
            title:       card.name,
            description: parsed.content,
            category:    parsed.category || 'Ginecologia',
            tags:        parsed.tags     || '',
            read_time:   parsed.tempo    || '5',
            date:        getTodayDate()
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

function parseCardDescription(desc) {
  const lines = desc.split('\n');
  const meta  = {};
  let contentStart = 0;

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

  meta.content = lines.slice(contentStart).join('\n').trim();
  return meta;
}

function getTodayDate() {
  const d = new Date();
  return `${String(d.getDate()).padStart(2,'0')}/${String(d.getMonth()+1).padStart(2,'0')}/${d.getFullYear()}`;
}
