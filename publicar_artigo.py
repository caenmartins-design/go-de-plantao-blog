#!/usr/bin/env python3
import sys
from pathlib import Path
from publicar import publish_article

body_html = """<p>O contato pele a pele (CPP) precoce é reconhecido mundialmente como uma intervenção de alta eficácia e baixo custo para melhorar desfechos de saúde tanto para as mães quanto para os recém-nascidos. Em 2026, o Ministério da Saúde do Brasil publicou a <strong>Nota Técnica nº 98/2026-DAHUD/SAES/MS</strong>, atualizando as diretrizes nacionais para a implementação do contato pele a pele imediatamente após o nascimento. A nova regulamentação traz mudanças estruturais importantes no fluxo de atendimento na sala de parto e no centro cirúrgico.</p>

<h2>O que estabelece a nova Nota Técnica nº 98/2026?</h2>
<p>A diretriz principal da Nota Técnica é clara: <strong>o contato pele a pele imediato e ininterrupto na primeira hora de vida deve ser a regra, e a separação mãe-bebê deve ser a exceção</strong>. A recomendação aplica-se a todos os nascimentos no território nacional que atendam aos critérios clínicos de estabilidade.</p>

<div class="callout">
  <div class="callout-title">Quem é elegível para o CPP imediato?</div>
  Todos os recém-nascidos clinicamente estáveis, o que inclui explicitamente:
  <ul>
    <li>Nascimentos por <strong>parto vaginal</strong></li>
    <li>Nascimentos por <strong>cesariana</strong></li>
    <li>Gestações <strong>gemelares</strong> (onde ambos os bebês nasçam estáveis)</li>
    <li><strong>Prematuros tardios ou moderados</strong> que apresentem boa vitalidade ao nascer</li>
  </ul>
</div>

<h2>Preservando a "Hora de Ouro" (Golden Hour)</h2>
<p>A primeira hora de vida pós-natal é um período crítico de transição fisiológica e adaptação extrauterina, conhecida na literatura médica como a <strong>"Hora de Ouro"</strong>. O Ministério da Saúde, em consonância com as recomendações da Organização Mundial da Saúde (OMS), reforça o conceito de <strong>"Zero Separação"</strong> mãe-bebê.</p>
<p>Durante esses primeiros 60 minutos, as prioridades ininterruptas de atendimento ao binômio estável são:</p>
<ol>
  <li><strong>Clampeamento oportuno do cordão umbilical:</strong> realizado entre 1 e 3 minutos (ou após cessar a pulsação), exceto em situações específicas onde haja indicação de clampeamento imediato.</li>
  <li><strong>Contato pele a pele imediato:</strong> posicionar o recém-nascido nu, de bruços, diretamente sobre o tórax ou abdômen despido da mãe, cobrindo-o com um campo aquecido e seco.</li>
  <li><strong>Início precoce da amamentação:</strong> apoiar a mãe e o bebê para que o primeiro aleitamento ocorra de forma espontânea ainda durante esta primeira hora de contato físico.</li>
</ol>

<h2>O que pode esperar? Postergar procedimentos de rotina</h2>
<p>Para viabilizar o contato pele a pele ininterrupto, a Nota Técnica recomenda formalmente que todos os procedimentos de rotina que impliquem na separação do binômio sejam <strong>postergados</strong> para após a primeira hora de vida ou após a primeira mamada.</p>
<p>Devem ser postergados:</p>
<ul>
  <li><strong>Pesagem</strong> e mensuração de dados <strong>antropométricos</strong> (perímetro cefálico, torácico e comprimento);</li>
  <li>Administração de <strong>vacinas</strong> (como a vacina da Hepatite B);</li>
  <li>Administração de <strong>profilaxias neonatais</strong> (como a vitamina K intramuscular e o método Credé/nitrato de prata para profilaxia da oftalmia neonatal).</li>
</ul>
<p>A avaliação da vitalidade do recém-nascido (incluindo o boletim de Apgar do 1º e 5º minutos) deve ser realizada clinicamente pela equipe de neonatologia/pediatria enquanto o bebê permanece no colo materno, sem necessidade de levá-lo à mesa de reanimação.</p>

<h2>Benefícios do Contato Pele a Pele Baseados em Evidências</h2>
<p>O CPP imediato não é um ato meramente humanitário ou afetivo; trata-se de uma intervenção clínica com fortes bases fisiológicas e benefícios documentados na literatura médica:</p>

<table>
  <thead>
    <tr>
      <th>Benefícios para o Recém-Nascido</th>
      <th>Benefícios para a Mãe</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td><strong>Termorregulação eficaz:</strong> a pele da mãe funciona como uma barreira térmica ativa, reduzindo o risco de hipotermia neonatal.</td>
      <td><strong>Redução do tempo de dequitação:</strong> estimula a liberação endógena de ocitocina, acelerando o terceiro período do parto.</td>
    </tr>
    <tr>
      <td><strong>Controle glicêmico:</strong> diminui o estresse do nascimento, reduzindo o consumo de glicose e o risco de hipoglicemia.</td>
      <td><strong>Redução de hemorragias:</strong> a ocitocina liberada favorece a contração uterina no pós-parto imediato.</td>
    </tr>
    <tr>
      <td><strong>Estabilidade cardiorrespiratória:</strong> estabiliza a frequência cardíaca e respiratória do bebê mais rapidamente.</td>
      <td><strong>Efeito ansiolítico:</strong> reduz significativamente os níveis de cortisol (hormônio do estresse) e ansiedade materna.</td>
    </tr>
    <tr>
      <td><strong>Colonização protetora:</strong> o bebê é colonizado pela microbiota bacteriana da pele da mãe, em vez dos patógenos hospitalares.</td>
      <td><strong>Prevenção de depressão:</strong> o vínculo inicial e o contato precoce estão associados a menor taxa de depressão pós-parto.</td>
    </tr>
  </tbody>
</table>

<h2>Particularidades do Manejo na Cesariana</h2>
<p>Historicamente, a cesariana era um ambiente onde o contato pele a pele era frequentemente negligenciado devido a barreiras cirúrgicas ou de temperatura do bloco cirúrgico. A Nota Técnica nº 98/2026 estabelece diretrizes rígidas para reverter esse cenário:</p>
<ul>
  <li>O CPP deve ser iniciado <strong>o mais precocemente possível</strong> no centro cirúrgico;</li>
  <li>O recém-nascido estável deve permanecer posicionado no tórax materno <strong>durante todo o período de sutura e fechamento da parede abdominal</strong> da mãe;</li>
  <li>A equipe de anestesiologia e enfermagem deve garantir o posicionamento seguro do bebê e o monitoramento contínuo da estabilidade clínica da mãe e do recém-nascido.</li>
</ul>

<h2>O Papel do Pai ou Acompanhante no CPP</h2>
<div class="callout pink">
  <div class="callout-title">Novidade Regulatória Importante</div>
  Nos casos em que a mãe apresente intercorrências clínicas imediatas no pós-parto (por exemplo, necessidade de anestesia geral de urgência, sangramento excessivo sob intervenção ativa ou outra instabilidade que impeça fisicamente o contato), a Nota Técnica recomenda que o <strong>contato pele a pele imediato seja realizado com o pai ou acompanhante de escolha da gestante</strong>. Isso visa preservar a transição térmica e sensorial protetora para o bebê.
</div>

<h2>Adequação dos Serviços de Saúde</h2>
<p>A implementação dessas diretrizes exige uma reestruturação dos fluxos institucionais e o engajamento de equipes multiprofissionais (obstetras, pediatras, anestesiologistas, enfermeiras obstétricas e técnicos). Os serviços precisarão:</p>
<ol>
  <li><strong>Revisar protocolos internos:</strong> readequando a rotina de recepção do recém-nascido nas salas de parto e blocos cirúrgicos;</li>
  <li><strong>Capacitar as equipes:</strong> com treinamentos voltados ao posicionamento seguro do RN no tórax e detecção de sinais de alerta neonatais durante o CPP;</li>
  <li><strong>Registrar em prontuário:</strong> é obrigatório registrar em prontuário se o contato pele a pele foi realizado, sua duração e, em caso de não realização, a devida justificativa clínica.</li>
</ol>

<h2>Take Home Message para o Plantão</h2>
<ul>
  <li>🔑 <strong>Zero Separação:</strong> Todo recém-nascido estável deve ir direto para o tórax materno imediatamente ao nascimento.</li>
  <li>🔑 <strong>Procedimentos de Rotina Aguardam:</strong> Peso, comprimento, vitamina K e vacina de Hepatite B devem ser adiados para depois da primeira hora.</li>
  <li>🔑 <strong>Regra para Cesarianas:</strong> A cesariana não é contraindicação para o CPP; o bebê deve ficar com a mãe durante a sutura da cirurgia.</li>
  <li>🔑 <strong>Alternativa de Acompanhante:</strong> Na impossibilidade materna, o contato imediato deve ser feito com o pai ou acompanhante.</li>
</ul>"""

publish_article(
    title="Ministério da Saúde Atualiza Recomendações Sobre Contato Pele a Pele",
    category="Guidelines",
    body_html=body_html,
    excerpt="O Ministério da Saúde publicou a Nota Técnica nº 98/2026 estabelecendo o contato pele a pele imediato e ininterrupto como regra na sala de parto. Veja as mudanças para parto vaginal, cesariana, prematuros estáveis e gemelares.",
    tags=["contato pele a pele", "recém-nascido", "parto vaginal", "cesariana", "Nota Técnica 98/2026", "Ministério da Saúde", "humanização"],
    date="14/06/2026",
    reference_pdf="/Users/cae/Downloads/Nota Técnica nº 98.2026-DAHUD-SAES-MS.pdf",
    reference_title="Nota Técnica nº 98/2026-DAHUD/SAES/MS — Implementação do contato pele a pele imediatamente após o nascimento"
)
