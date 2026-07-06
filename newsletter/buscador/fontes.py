# Definição de todas as fontes de busca por categoria

RSS_FEEDS = [
    # ── Revistas Científicas ──────────────────────────────────
    {
        "nome": "BJOG",
        "url": "https://obgyn.onlinelibrary.wiley.com/feed/14710528/most-recent",
        "tipo": "artigo_cientifico",
        "idioma": "en",
    },
    {
        "nome": "American Journal of Obstetrics & Gynecology",
        "url": "https://www.ajog.org/rss/S0002-9378.xml",
        "tipo": "artigo_cientifico",
        "idioma": "en",
    },
    {
        "nome": "Obstetrics & Gynecology (ACOG)",
        "url": "https://journals.lww.com/greenjournal/rss/currentissue.xml",
        "tipo": "artigo_cientifico",
        "idioma": "en",
    },
    {
        "nome": "The Lancet",
        "url": "https://www.thelancet.com/rssfeed/lancet_current.xml",
        "tipo": "artigo_cientifico",
        "idioma": "en",
    },
    {
        "nome": "NEJM",
        "url": "https://www.nejm.org/action/showFeed?jc=nejm&type=etoc&feed=rss",
        "tipo": "artigo_cientifico",
        "idioma": "en",
    },
    {
        "nome": "JAMA Network Open",
        "url": "https://jamanetwork.com/journals/jamanetworkopen/rss",
        "tipo": "artigo_cientifico",
        "idioma": "en",
    },
    {
        "nome": "Ultrasound in Obstetrics & Gynecology",
        "url": "https://obgyn.onlinelibrary.wiley.com/feed/10970273/most-recent",
        "tipo": "artigo_cientifico",
        "idioma": "en",
    },
    {
        "nome": "Fertility and Sterility",
        "url": "https://www.fertstert.org/rss/S0015-0282.xml",
        "tipo": "artigo_cientifico",
        "idioma": "en",
    },
    {
        "nome": "Gynecologic Oncology",
        "url": "https://www.gynecologiconcology-online.net/rss/S0090-8258.xml",
        "tipo": "artigo_cientifico",
        "idioma": "en",
    },
    {
        "nome": "BMJ",
        "url": "https://www.bmj.com/rss/current.xml",
        "tipo": "artigo_cientifico",
        "idioma": "en",
    },
    # ── Sociedades Médicas ────────────────────────────────────
    {
        "nome": "ACOG News",
        "url": "https://www.acog.org/news/rss",
        "tipo": "diretriz",
        "idioma": "en",
    },
    {
        "nome": "WHO News",
        "url": "https://www.who.int/feeds/entity/mediacentre/news/en/rss.xml",
        "tipo": "diretriz",
        "idioma": "en",
    },
    {
        "nome": "CDC Women's Health",
        "url": "https://tools.cdc.gov/api/v2/resources/media/403372.rss",
        "tipo": "diretriz",
        "idioma": "en",
    },
    # ── Portais de Notícias Médicas ───────────────────────────
    {
        "nome": "Medscape OB/GYN",
        "url": "https://rss.medscape.com/rss/ob-gyn-news.xml",
        "tipo": "noticia",
        "idioma": "en",
    },
    {
        "nome": "MedPage Today",
        "url": "https://www.medpagetoday.com/rss/news.xml",
        "tipo": "noticia",
        "idioma": "en",
    },
    {
        "nome": "Science Daily — Pregnancy & Childbirth",
        "url": "https://www.sciencedaily.com/rss/health_medicine/pregnancy_and_childbirth.xml",
        "tipo": "noticia",
        "idioma": "en",
    },
    {
        "nome": "Science Daily — Women's Health",
        "url": "https://www.sciencedaily.com/rss/health_medicine/gynecology.xml",
        "tipo": "noticia",
        "idioma": "en",
    },
    {
        "nome": "Reuters Health",
        "url": "https://feeds.reuters.com/reuters/healthNews",
        "tipo": "noticia",
        "idioma": "en",
    },
    # ── Portais Brasileiros ───────────────────────────────────
    {
        "nome": "Folha Equilíbrio e Saúde",
        "url": "https://feeds.folha.uol.com.br/equilibrioesaude/rss091.xml",
        "tipo": "noticia",
        "idioma": "pt",
    },
    {
        "nome": "G1 Ciência e Saúde",
        "url": "https://g1.globo.com/rss/g1/ciencia-e-saude/",
        "tipo": "noticia",
        "idioma": "pt",
    },
    {
        "nome": "BBC Brasil",
        "url": "https://feeds.bbci.co.uk/portuguese/rss.xml",
        "tipo": "noticia",
        "idioma": "pt",
    },
    {
        "nome": "Agência Saúde (MS)",
        "url": "https://www.gov.br/saude/pt-br/assuntos/noticias/@@rss.xml",
        "tipo": "diretriz",
        "idioma": "pt",
    },
    {
        "nome": "CNN Brasil Saúde",
        "url": "https://www.cnnbrasil.com.br/saude/feed/",
        "tipo": "noticia",
        "idioma": "pt",
    },
    {
        "nome": "Exame Ciência",
        "url": "https://exame.com/ciencia/feed/",
        "tipo": "noticia",
        "idioma": "pt",
    },
]

# Fontes que requerem scraping direto (sem RSS útil)
SCRAPING_FONTES = [
    {
        "nome": "FEBRASGO Notícias",
        "url": "https://www.febrasgo.org.br/noticias",
        "seletor_itens": "div.noticias-item, article.noticia, .card-noticia",
        "seletor_titulo": "h2, h3, .titulo",
        "seletor_link": "a",
        "seletor_data": "time, .data, span.date",
        "tipo": "diretriz",
        "idioma": "pt",
    },
    {
        "nome": "Revista Femina",
        "url": "https://www.revistafemina.com.br/artigos",
        "seletor_itens": "article, .artigo-item, .post-card",
        "seletor_titulo": "h2, h3, .entry-title",
        "seletor_link": "a",
        "seletor_data": "time, .post-date, .entry-date",
        "tipo": "artigo_cientifico",
        "idioma": "pt",
    },
]

# Termos de busca no PubMed para GO
PUBMED_QUERY = (
    '(obstetrics[MeSH Terms] OR gynecology[MeSH Terms] OR '
    '"maternal health"[MeSH Terms] OR "pregnancy complications"[MeSH Terms] OR '
    'endometriosis[MeSH Terms] OR "uterine fibroids"[MeSH Terms] OR '
    '"ovarian neoplasms"[MeSH Terms] OR "cervical neoplasms"[MeSH Terms] OR '
    '"breast neoplasms"[MeSH Terms] OR "preeclampsia"[MeSH Terms] OR '
    '"postpartum hemorrhage"[MeSH Terms] OR menopause[MeSH Terms] OR '
    '"contraception"[MeSH Terms] OR "infertility"[MeSH Terms]) '
    'AND ("last 7 days"[PDat]) AND (Clinical Trial[pt] OR Randomized Controlled Trial[pt] '
    'OR Meta-Analysis[pt] OR Systematic Review[pt] OR Guideline[pt] OR Review[pt])'
)

# Palavras-chave para filtrar artigos de feeds gerais (RSS não-específico)
KEYWORDS_OBGYN = [
    # Português
    "gestação", "gravidez", "grávida", "parto", "puerpério", "pós-parto",
    "ginecologia", "obstetrícia", "obstetricia", "ginecologista", "obstetra",
    "menopausa", "climatério", "endometriose", "mioma", "útero", "ovário",
    "placenta", "pré-eclâmpsia", "eclâmpsia", "preeclâmpsia",
    "amamentação", "aleitamento", "anticoncepção", "contraceptivo",
    "DIU", "implante subdérmico", "etonogestrel",
    "câncer cervical", "câncer de mama", "colo do útero", "HPV",
    "fertilização", "FIV", "reprodução assistida", "infertilidade",
    "hemorragia pós-parto", "HPP", "mortalidade materna",
    "pré-natal", "prenatal", "ultrassom obstétrico", "doppler",
    "cesárea", "cesária", "vaginal", "fórcipe", "VBAC",
    "triagem neonatal", "diabetes gestacional",
    "síndrome dos ovários policísticos", "SOP", "PCOS",
    "aborto", "abortamento", "miscarriage",
    "vulvovaginite", "vaginose", "corrimento",
    "progesterona", "estrogênio", "TRH",
    # Inglês
    "obstetrics", "gynecology", "gynaecology", "obstetric", "gynecologic",
    "pregnancy", "pregnant", "prenatal", "antenatal", "postnatal",
    "postpartum", "maternal", "fetal", "foetal",
    "menopause", "endometriosis", "uterine", "ovarian",
    "placenta", "preeclampsia", "eclampsia",
    "breastfeeding", "lactation", "contraception", "IUD",
    "cervical cancer", "ovarian cancer", "breast cancer", "HPV",
    "IVF", "infertility", "fertility", "miscarriage",
    "postpartum hemorrhage", "maternal mortality",
    "cesarean", "caesarean", "vaginal delivery",
    "gestational diabetes", "PCOS", "polycystic",
]
