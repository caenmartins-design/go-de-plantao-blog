const Anthropic = require('@anthropic-ai/sdk');
const fs = require('fs');
const path = require('path');
const https = require('https');

const BLOG_ROOT = path.join(__dirname, '..', '..');

function downloadFile(url, destPath, headers = {}, redirectCount = 0) {
  return new Promise((resolve, reject) => {
    if (redirectCount > 5) return reject(new Error('Excesso de redirecionamentos ao baixar PDF'));
    https.get(url, { headers }, (res) => {
      if (res.statusCode >= 300 && res.statusCode < 400 && res.headers.location) {
        res.resume();
        // não repassa headers de auth do Trello para o destino do redirect (ex.: CDN assinada)
        return resolve(downloadFile(res.headers.location, destPath, {}, redirectCount + 1));
      }
      if (res.statusCode !== 200) {
        res.resume();
        return reject(new Error(`Falha ao baixar PDF (HTTP ${res.statusCode})`));
      }
      const fileStream = fs.createWriteStream(destPath);
      res.pipe(fileStream);
      fileStream.on('finish', () => fileStream.close(resolve));
      fileStream.on('error', reject);
    }).on('error', reject);
  });
}

function generateSlug(title) {
  return title
    .toLowerCase()
    .normalize('NFD')
    .replace(/[̀-ͯ]/g, '')
    .replace(/[^a-z0-9\s-]/g, '')
    .replace(/\s+/g, '-')
    .replace(/-+/g, '-')
    .trim()
    .substring(0, 80);
}

function buildArticleHTML(slug, title, category, date, readTime, articleBody, metaDescription, tags) {
  const tagsHtml = tags.map(t => `<span class="tag">${t.trim()}</span>`).join(' ');

  return `<!DOCTYPE html>
<html lang="pt-BR">
<head>
  <!-- Google tag (gtag.js) -->
  <script async src="https://www.googletagmanager.com/gtag/js?id=G-VEG94VC9YR"></script>
  <script>
    window.dataLayer = window.dataLayer || [];
    function gtag(){dataLayer.push(arguments);}
    gtag('js', new Date());
    gtag('config', 'G-VEG94VC9YR');
  </script>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>${title} — Go de Plantão</title>
  <meta name="description" content="${metaDescription}" />
  <link rel="stylesheet" href="../style.css" />
</head>
<body>

  <header class="site-header">
    <div class="header-inner">
      <a href="/" class="site-logo">
        <img src="../logo.png" alt="Go de Plantão" class="logo-img" onerror="this.style.display='none';this.nextElementSibling.style.display='flex'">
        <div class="logo-badge" style="display:none">GO</div>
        <div class="logo-text">
          <strong>Go de Plantão</strong>
          <span>Ginecologia &amp; Obstetrícia</span>
        </div>
      </a>
      <nav class="header-nav">
        <a href="/">Blog</a>
        <a href="/newsletters.html">Newsletters</a>
        <a href="/ferramentas/conduta-colo-do-utero">Ferramentas</a>
        <a href="https://med.estrategia.com/concursos/cursos/cursos-de-ginecologia-e-obstetricia" target="_blank" rel="noopener">Cursos</a>
      </nav>
    </div>
  </header>

  <div class="promo-banner-wrap" id="toolPromoBanner">
    <div class="promo-banner">
      <button class="promo-close" type="button" onclick="(function(){var b=document.getElementById('toolPromoBanner');if(b)b.remove();try{sessionStorage.setItem('toolPromoClosed','1')}catch(e){}})()" aria-label="Fechar aviso">&times;</button>
      <span class="promo-badge">🔬 Novidade</span>
      <div class="promo-content">
        <div class="promo-text">
          <div class="promo-label">Ferramenta interativa</div>
          <div class="promo-title">Conduta no rastreamento do colo do útero</div>
          <p class="promo-sub">Informe o genótipo do HPV e o achado da colposcopia — receba a conduta na hora, com base nas novas Diretrizes Brasileiras.</p>
        </div>
        <div class="promo-cta">
          <a href="/ferramentas/conduta-colo-do-utero" class="promo-btn">Testar agora →</a>
        </div>
      </div>
    </div>
  </div>
  <script>
    (function(){
      try { if (sessionStorage.getItem('toolPromoClosed')) { var b = document.getElementById('toolPromoBanner'); if (b) b.remove(); } } catch(e){}
    })();
  </script>

  <main class="article-page">

    <nav class="article-breadcrumb">
      <a href="/">Blog</a> › <a href="/">${category}</a> › ${title}
    </nav>

    <header class="article-header">
      <span class="article-category">${category}</span>
      <h1 class="article-title">${title}</h1>
      <div class="article-meta">
        <span>📅 ${date}</span>
        <span>⏱ ${readTime} min de leitura</span>
        <span>🏥 Go de Plantão</span>
      </div>
      <div class="article-divider"></div>
    </header>

    <article class="article-body">
${articleBody}
    </article>

    <div class="article-tags">
      ${tagsHtml}
    </div>

    <div class="article-cta">
      <h3>Quer dominar Ginecologia e Obstetrícia?</h3>
      <p>Acesse os cursos do Estratégia MED com conteúdo atualizado, didático e focado no que realmente importa.</p>
      <div class="coupon-badge">GODEPLANTAO</div>
      <br>
      <a class="cta-btn" href="https://med.estrategia.com/concursos/cursos/cursos-de-ginecologia-e-obstetricia" target="_blank" rel="noopener">
        🎓 Acessar cursos de GO com desconto
      </a>
    </div>

  </main>

  <footer class="site-footer">
    <p><strong>Go de Plantão</strong> — Conteúdo educacional em Ginecologia e Obstetrícia</p>
    <p style="margin-top:8px">Use o cupom <strong>GODEPLANTAO</strong> nos <a href="https://med.estrategia.com/concursos/cursos/cursos-de-ginecologia-e-obstetricia" target="_blank">cursos do Estratégia MED</a></p>
  </footer>

<nav class="mobile-tabbar">
  <a href="/" class="tab-item active">
    <span class="icon-wrap"><svg class="tab-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/><line x1="16" y1="13" x2="8" y2="13"/><line x1="16" y1="17" x2="8" y2="17"/></svg></span>
    <span class="tab-label">Artigos</span>
  </a>
  <a href="/newsletters.html" class="tab-item">
    <span class="icon-wrap"><svg class="tab-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M4 4h16c1.1 0 2 .9 2 2v12c0 1.1-.9 2-2 2H4c-1.1 0-2-.9-2-2V6c0-1.1.9-2 2-2z"/><polyline points="22 6 12 13 2 6"/></svg></span>
    <span class="tab-label">Newsletter</span>
  </a>
  <a href="/ferramentas/conduta-colo-do-utero" class="tab-item">
    <span class="icon-wrap"><svg class="tab-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="22 12 18 12 15 21 9 3 6 12 2 12"/></svg></span>
    <span class="tab-label">Ferramentas</span>
  </a>
</nav>
<script>
if ('serviceWorker' in navigator) {
  window.addEventListener('load', () => navigator.serviceWorker.register('/sw.js'));
}
</script>
</body>
</html>`;
}

function updateArtigos(slug, title, category, excerpt, date, readTime, tags) {
  const filePath = path.join(BLOG_ROOT, 'artigos.json');
  const artigos = JSON.parse(fs.readFileSync(filePath, 'utf8'));

  artigos.unshift({
    slug,
    title,
    category,
    excerpt,
    date,
    read_time: parseInt(readTime) || 5,
    tags: tags.map(t => t.trim()).filter(Boolean)
  });

  fs.writeFileSync(filePath, JSON.stringify(artigos, null, 2));
  console.log('✓ artigos.json atualizado');
}

function updateIndex(slug, title, category, date, readTime, excerpt) {
  const filePath = path.join(BLOG_ROOT, 'index.html');
  let html = fs.readFileSync(filePath, 'utf8');

  const newCard = `
        <article class="article-card">
          <div class="card-body">
            <div class="card-meta">
              <span class="card-category">${category}</span>
              <span>${date}</span>
            </div>
            <h2 class="card-title">${title}</h2>
            <p class="card-excerpt">${excerpt}</p>
            <div class="card-footer">
              <a class="read-more" href="artigos/${slug}.html">Leia o artigo →</a>
              <span class="read-time">⏱ ${readTime} min</span>
            </div>
          </div>
        </article>
`;

  html = html.replace(
    '<div class="articles-grid" id="articles-grid">',
    '<div class="articles-grid" id="articles-grid">' + newCard
  );

  fs.writeFileSync(filePath, html);
  console.log('✓ index.html atualizado');
}

async function main() {
  const title            = process.env.CARD_TITLE;
  const description      = process.env.CARD_DESCRIPTION;
  const categoryOverride = process.env.CARD_CATEGORY || '';
  const tagsOverride     = process.env.CARD_TAGS || '';
  const readTimeOverride = process.env.CARD_READ_TIME || '';
  const date             = process.env.CARD_DATE;

  if (!title || !description) {
    throw new Error('CARD_TITLE e CARD_DESCRIPTION são obrigatórios');
  }

  const slug = generateSlug(title);

  const articlePath = path.join(BLOG_ROOT, 'artigos', `${slug}.html`);
  if (fs.existsSync(articlePath)) {
    console.log(`⚠️  Artigo já existe: artigos/${slug}.html — ignorando duplicata.`);
    process.exit(0);
  }

  console.log(`Gerando artigo: "${title}" (${slug})`);

  let pdfRelPath = null;
  const pdfUrl      = process.env.CARD_PDF_URL;
  const pdfIsUpload = process.env.CARD_PDF_IS_UPLOAD === 'true';

  if (pdfUrl && pdfIsUpload) {
    // Arquivo hospedado no Trello: precisa de auth para download
    const trelloKey   = process.env.TRELLO_API_KEY;
    const trelloToken = process.env.TRELLO_TOKEN;
    if (!trelloKey || !trelloToken) {
      throw new Error('PDF no Trello detectado, mas TRELLO_API_KEY/TRELLO_TOKEN não estão configurados nos secrets');
    }
    const pdfsDir    = path.join(BLOG_ROOT, 'pdfs');
    fs.mkdirSync(pdfsDir, { recursive: true });
    const pdfFileName = `${slug}.pdf`;
    // O endpoint de download de anexo do Trello não aceita key/token via query string
    // (retorna 401) — precisa do header Authorization: OAuth.
    const authHeader = { Authorization: `OAuth oauth_consumer_key="${trelloKey}", oauth_token="${trelloToken}"` };
    await downloadFile(pdfUrl, path.join(pdfsDir, pdfFileName), authHeader);
    pdfRelPath = `pdfs/${pdfFileName}`;
    console.log(`✓ PDF baixado do Trello: ${pdfRelPath}`);
  } else if (pdfUrl) {
    // Link externo (Google Drive, Dropbox etc.): usa a URL diretamente
    pdfRelPath = pdfUrl;
    console.log(`✓ PDF externo: ${pdfRelPath}`);
  }

  const client = new Anthropic();

  const system = `Você é o redator médico do blog Go de Plantão, especializado em Ginecologia e Obstetrícia.
Seu trabalho é transformar roteiros clínicos em artigos médicos de alta qualidade em HTML.

REGRAS DE CONTEÚDO:
- Tom clínico, direto, sem jargão desnecessário
- Sem comentários no HTML
- Use <h2> para seções principais, <h3> para subseções
- Listas: <ul> ou <ol>; dados comparativos: <table>
- Destaques clínicos: <div class="callout"><div class="callout-title">Título</div>Conteúdo</div>
- Dados numéricos de destaque: <blockquote>
- Termine sempre com <h2>Conclusão</h2> com callout "Take Home Message"
- Referência bibliográfica no final: <p><em>Referência: ...</em></p>
- Não inclua a tag <article> em si, apenas o conteúdo interno

Quando categoria, tags e/ou tempo de leitura não vierem definidos manualmente, decida você mesmo com base no roteiro:
- categoria: escolha a mais adequada dentre as já usadas no blog (Ginecologia, Obstetrícia, Rastreamento, Guidelines, Saúde Pública); só crie uma nova categoria, curta e específica, se nenhuma dessas servir
- tags: de 3 a 6 palavras-chave curtas e relevantes para o tema
- tempo de leitura: estimativa em minutos (número inteiro), coerente com o tamanho do roteiro

RETORNE SOMENTE JSON VÁLIDO no seguinte formato (sem markdown, sem blocos de código):
{
  "meta_description": "descrição SEO com até 155 caracteres",
  "excerpt": "resumo com até 220 caracteres para o card da homepage",
  "category": "categoria sugerida (ignorada se já veio definida manualmente)",
  "tags": ["tag1", "tag2", "tag3"],
  "read_time": 5,
  "article_body_html": "HTML completo do corpo do artigo"
}`;

  const category = categoryOverride
    ? `Categoria (definida manualmente): ${categoryOverride}`
    : 'Categoria: não informada — decida com base no roteiro';
  const tags = tagsOverride
    ? `Tags (definidas manualmente): ${tagsOverride}`
    : 'Tags: não informadas — decida com base no roteiro';
  const readTime = readTimeOverride
    ? `Tempo de leitura (definido manualmente): ${readTimeOverride} min`
    : 'Tempo de leitura: não informado — decida com base no roteiro';

  const response = await client.messages.create({
    model: 'claude-sonnet-4-6',
    max_tokens: 8000,
    system,
    messages: [{
      role: 'user',
      content: `Título: ${title}
${category}
${tags}
Data: ${date}
${readTime}

Roteiro:
${description}`
    }]
  });

  const text = response.content[0].text.trim();
  const jsonMatch = text.match(/\{[\s\S]*\}/);
  if (!jsonMatch) throw new Error('Claude não retornou JSON válido:\n' + text);

  const parsed = JSON.parse(jsonMatch[0]);
  const { meta_description, excerpt, article_body_html } = parsed;

  const finalCategory = categoryOverride || parsed.category || 'Ginecologia';
  const finalTags = (tagsOverride
    ? tagsOverride.split(',')
    : (Array.isArray(parsed.tags) ? parsed.tags : [])
  ).map(t => t.trim()).filter(Boolean);
  const finalReadTime = readTimeOverride || String(parsed.read_time || 5).replace(/\D/g, '') || '5';

  let bodyHtml = article_body_html;
  if (pdfRelPath) {
    const href = pdfRelPath.startsWith('http') ? pdfRelPath : `../${pdfRelPath}`;
    const downloadBlock = `    <div class="callout">
      <div class="callout-title">📄 Baixe o material completo</div>
      <p>O PDF completo está disponível para download gratuito.</p>
      <a class="cta-btn" href="${href}" target="_blank" rel="noopener">⬇️ Baixar PDF completo</a>
    </div>
`;
    bodyHtml = downloadBlock + bodyHtml;
  }

  const articleHtml = buildArticleHTML(
    slug, title, finalCategory, date, finalReadTime,
    bodyHtml, meta_description, finalTags
  );

  fs.writeFileSync(articlePath, articleHtml);
  console.log(`✓ artigos/${slug}.html criado`);

  updateArtigos(slug, title, finalCategory, excerpt, date, finalReadTime, finalTags);
  updateIndex(slug, title, finalCategory, date, finalReadTime, excerpt);

  console.log('✅ Publicação concluída!');
}

main().catch(err => {
  console.error('❌ Erro:', err.message);
  process.exit(1);
});
