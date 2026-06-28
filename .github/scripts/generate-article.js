const Anthropic = require('@anthropic-ai/sdk');
const fs = require('fs');
const path = require('path');

const BLOG_ROOT = path.join(__dirname, '..', '..');

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
        <a href="https://med.estrategia.com/concursos/cursos/cursos-de-ginecologia-e-obstetricia" target="_blank" rel="noopener">Cursos</a>
      </nav>
    </div>
  </header>

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
  const title       = process.env.CARD_TITLE;
  const description = process.env.CARD_DESCRIPTION;
  const category    = process.env.CARD_CATEGORY || 'Ginecologia';
  const tagsRaw     = process.env.CARD_TAGS || '';
  const readTime    = process.env.CARD_READ_TIME || '5';
  const date        = process.env.CARD_DATE;

  if (!title || !description) {
    throw new Error('CARD_TITLE e CARD_DESCRIPTION são obrigatórios');
  }

  const tags = tagsRaw.split(',').map(t => t.trim()).filter(Boolean);
  const slug = generateSlug(title);

  const articlePath = path.join(BLOG_ROOT, 'artigos', `${slug}.html`);
  if (fs.existsSync(articlePath)) {
    console.log(`⚠️  Artigo já existe: artigos/${slug}.html — ignorando duplicata.`);
    process.exit(0);
  }

  console.log(`Gerando artigo: "${title}" (${slug})`);

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

RETORNE SOMENTE JSON VÁLIDO no seguinte formato (sem markdown, sem blocos de código):
{
  "meta_description": "descrição SEO com até 155 caracteres",
  "excerpt": "resumo com até 220 caracteres para o card da homepage",
  "article_body_html": "HTML completo do corpo do artigo"
}`;

  const response = await client.messages.create({
    model: 'claude-sonnet-4-6',
    max_tokens: 8000,
    system,
    messages: [{
      role: 'user',
      content: `Título: ${title}
Categoria: ${category}
Tags: ${tags.join(', ')}
Data: ${date}
Tempo de leitura: ${readTime} min

Roteiro:
${description}`
    }]
  });

  const text = response.content[0].text.trim();
  const jsonMatch = text.match(/\{[\s\S]*\}/);
  if (!jsonMatch) throw new Error('Claude não retornou JSON válido:\n' + text);

  const { meta_description, excerpt, article_body_html } = JSON.parse(jsonMatch[0]);

  const articleHtml = buildArticleHTML(
    slug, title, category, date, readTime,
    article_body_html, meta_description, tags
  );

  fs.writeFileSync(articlePath, articleHtml);
  console.log(`✓ artigos/${slug}.html criado`);

  updateArtigos(slug, title, category, excerpt, date, readTime, tags);
  updateIndex(slug, title, category, date, readTime, excerpt);

  console.log('✅ Publicação concluída!');
}

main().catch(err => {
  console.error('❌ Erro:', err.message);
  process.exit(1);
});
