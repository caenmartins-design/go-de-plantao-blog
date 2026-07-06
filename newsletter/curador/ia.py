"""Curadoria e sumarização de artigos com Claude (Anthropic API)."""

import json
import textwrap

import anthropic

from config import ANTHROPIC_API_KEY, MAX_NEWSLETTER

SYSTEM_PROMPT = textwrap.dedent("""
    Você é o curador científico do "GO de Plantão", perfil de divulgação médica em
    Ginecologia e Obstetrícia para médicos e estudantes de medicina no Brasil.

    Sua missão é analisar uma lista de artigos/notícias brutas coletadas de fontes
    internacionais e nacionais, e produzir uma curadoria semanal de alta qualidade.

    CRITÉRIOS DE SELEÇÃO (ordene por impacto):
    1. Ensaios clínicos randomizados ou meta-análises com resultado que muda conduta
    2. Novas diretrizes ou atualizações de sociedades (ACOG, FIGO, FEBRASGO, WHO, MS)
    3. Aprovações de medicamentos ou tecnologias pela ANVISA, FDA ou EMA relevantes para GO
    4. Notícias de saúde pública com impacto em saúde da mulher no Brasil
    5. Estudos observacionais de alto impacto (N grande, revista de primeiro quartil)

    DESCARTE sem hesitar:
    - Artigos sobre doenças sem relação com saúde da mulher ou GO
    - Artigos em pré-print sem revisão por pares
    - Notícias duplicadas ou muito similares (mantenha apenas a mais completa)
    - Artigos sem resumo útil

    FORMATO DE SAÍDA — JSON puro, sem markdown, sem explicações fora do JSON.
    Retorne exatamente este schema (array de objetos):

    [
      {
        "id": "<id original do artigo>",
        "titulo_pt": "<título em português, claro e direto>",
        "fonte": "<nome da fonte original>",
        "url": "<url original>",
        "categoria": "<Obstetrícia|Ginecologia|Oncologia Ginecológica|Medicina Fetal|Climatério|Contracepção|Saúde Pública>",
        "tipo": "<artigo_cientifico|diretriz|noticia|evento>",
        "destaque": <true apenas para O artigo mais impactante da semana, false para os demais>,
        "resumo": "<resumo em português, 2-3 parágrafos concisos para audiência médica. Contexto clínico, resultados principais e limitações se relevante>",
        "por_que_importa": "<1-2 frases explicando o impacto prático para o médico brasileiro>",
        "ponto_chave": "<1 frase — o take-home message mais importante>"
      }
    ]

    Regras de escrita:
    - Português brasileiro culto, mas acessível
    - Sem jargão desnecessário; explique termos técnicos em 1-2 palavras
    - Tom científico e respeitoso, sem sensacionalismo
    - Nunca invente dados, p-valores ou nomes de medicamentos não mencionados
    - Se o resumo bruto for insuficiente, use apenas o que está disponível
    - Seja conciso nos resumos — qualidade acima de quantidade
""").strip()

# Limite de artigos por lote enviado ao Claude
_LOTE_MAX = 25


def curar_artigos(artigos_brutos, max_items=MAX_NEWSLETTER):
    """
    Usa Claude para filtrar, traduzir e sumarizar artigos.
    Se houver mais de _LOTE_MAX artigos, processa em lotes e mescla os resultados.
    Retorna lista curada pronta para a newsletter.
    """
    if not artigos_brutos:
        print("Curador: nenhum artigo para processar.")
        return []

    if not ANTHROPIC_API_KEY:
        raise ValueError("ANTHROPIC_API_KEY não configurada no .env")

    client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
    lista_para_curar = _preparar_lista(artigos_brutos)

    if len(lista_para_curar) <= _LOTE_MAX:
        return _chamar_claude(client, lista_para_curar, max_items)

    # Processa em lotes e depois faz curadoria final
    print(f"Curador: {len(lista_para_curar)} artigos — processando em lotes de {_LOTE_MAX}...")
    candidatos = []
    for i in range(0, len(lista_para_curar), _LOTE_MAX):
        lote = lista_para_curar[i:i + _LOTE_MAX]
        parcial = _chamar_claude(client, lote, max_items)
        candidatos.extend(parcial)
        print(f"  Lote {i // _LOTE_MAX + 1}: {len(parcial)} selecionados")

    if len(candidatos) <= max_items:
        return candidatos

    # Curadoria final sobre os melhores candidatos
    print(f"Curador: curadoria final sobre {len(candidatos)} candidatos...")
    return _chamar_claude(client, _artigos_para_lista(candidatos), max_items)


def _chamar_claude(client, lista, max_items):
    """Envia um lote de artigos ao Claude e retorna os curados."""
    user_prompt = (
        f"Analise os seguintes {len(lista)} artigos/notícias coletados esta semana "
        f"e selecione os {max_items} mais relevantes para a newsletter semanal de GO.\n\n"
        f"ARTIGOS BRUTOS:\n{json.dumps(lista, ensure_ascii=False, indent=2)}"
    )

    print(f"Curador: enviando {len(lista)} artigos para o Claude...")

    try:
        resposta = client.messages.create(
            model="claude-opus-4-8",
            max_tokens=16000,
            system=SYSTEM_PROMPT,
            messages=[{"role": "user", "content": user_prompt}],
        )
        texto = resposta.content[0].text.strip()
        curados = _parsear_resposta(texto)
        print(f"Curador: {len(curados)} artigos selecionados.")
        return curados

    except anthropic.APIError as e:
        print(f"Curador erro API: {e}")
        raise


def _preparar_lista(artigos):
    """Simplifica artigos brutos para o contexto do Claude (economiza tokens)."""
    return [
        {
            "id":           a.get("id", ""),
            "titulo":       a.get("titulo", ""),
            "fonte":        a.get("fonte", ""),
            "url":          a.get("url", ""),
            "data":         a.get("data", ""),
            "resumo_bruto": a.get("resumo_bruto", "")[:400],
            "tipo":         a.get("tipo", ""),
            "idioma":       a.get("idioma", "en"),
        }
        for a in artigos
        if a.get("titulo")
    ]


def _artigos_para_lista(artigos_curados):
    """Converte artigos já curados de volta ao formato de lista para re-curadoria."""
    return [
        {
            "id":           a.get("id", ""),
            "titulo":       a.get("titulo_pt", a.get("titulo", "")),
            "fonte":        a.get("fonte", ""),
            "url":          a.get("url", ""),
            "data":         "",
            "resumo_bruto": a.get("resumo", "")[:400],
            "tipo":         a.get("tipo", ""),
            "idioma":       "pt",
        }
        for a in artigos_curados
        if a.get("titulo_pt") or a.get("titulo")
    ]


def _parsear_resposta(texto):
    """Extrai o JSON da resposta do Claude. Tenta recuperar JSON parcial se truncado."""
    texto = texto.strip()
    if texto.startswith("```"):
        linhas = texto.split("\n")
        texto = "\n".join(linhas[1:-1] if linhas[-1].strip() == "```" else linhas[1:])

    try:
        curados = json.loads(texto)
        if isinstance(curados, list):
            return curados
    except json.JSONDecodeError as e:
        print(f"Curador: erro ao parsear JSON — {e}")
        # Tenta recuperar objetos completos do JSON truncado
        recuperados = _recuperar_json_parcial(texto)
        if recuperados:
            print(f"Curador: recuperados {len(recuperados)} objetos do JSON truncado.")
            return recuperados
        print(f"Resposta recebida (início):\n{texto[:400]}")
    return []


def _recuperar_json_parcial(texto):
    """Extrai objetos JSON completos de uma resposta truncada."""
    objetos = []
    profundidade = 0
    inicio = None
    for i, c in enumerate(texto):
        if c == "{":
            if profundidade == 0:
                inicio = i
            profundidade += 1
        elif c == "}":
            profundidade -= 1
            if profundidade == 0 and inicio is not None:
                fragmento = texto[inicio:i + 1]
                try:
                    obj = json.loads(fragmento)
                    objetos.append(obj)
                except json.JSONDecodeError:
                    pass
                inicio = None
    return objetos
