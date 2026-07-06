/**
 * GO de Plantão — Sincroniza inscrições do Google Forms com o Google Contacts.
 *
 * Como instalar:
 * 1. Abra a planilha de respostas do Google Forms.
 * 2. Menu Extensões → Apps Script.
 * 3. Apague o conteúdo padrão do arquivo Code.gs e cole este arquivo inteiro.
 * 4. No editor, clique em "Serviços" (ícone +) → adicione "People API"
 *    (deixe o identificador como "People").
 * 5. Ajuste GRUPO_NOME abaixo se o rótulo no Google Contacts tiver outro nome.
 * 6. Menu Acionadores (relógio na lateral) → "+ Adicionar acionador":
 *      Função: onFormSubmit
 *      Evento: Do formulário — Ao enviar formulário
 *    Salve e autorize o script quando solicitado (é a sua própria conta Google).
 */

const GRUPO_NOME = 'GO de Plantão';

function onFormSubmit(e) {
  const respostas = e.namedValues;
  const nome  = (respostas['Nome']   && respostas['Nome'][0])   || '';
  const email = (respostas['E-mail'] && respostas['E-mail'][0]) || '';

  if (!email) {
    console.log('Envio sem e-mail, ignorado.');
    return;
  }

  const grupoResourceName = obterOuCriarGrupo_(GRUPO_NOME);
  const pessoaExistente   = buscarContatoPorEmail_(email);

  const resourceName = pessoaExistente
    ? pessoaExistente.resourceName
    : criarContato_(nome, email);

  adicionarAoGrupo_(resourceName, grupoResourceName);
  console.log(`Contato sincronizado: ${email}`);
}

function obterOuCriarGrupo_(nomeGrupo) {
  const resposta = People.ContactGroups.list({ pageSize: 200 });
  const grupos = resposta.contactGroups || [];

  for (const grupo of grupos) {
    if (grupo.name === nomeGrupo) return grupo.resourceName;
  }

  const criado = People.ContactGroups.create({ contactGroup: { name: nomeGrupo } });
  return criado.resourceName;
}

function buscarContatoPorEmail_(email) {
  // A API de busca de contatos precisa de um warm-up (primeira chamada pode não indexar ainda).
  const resultado = People.People.searchContacts({
    query: email,
    readMask: 'names,emailAddresses',
  });

  const resultados = resultado.results || [];
  for (const item of resultados) {
    const emails = item.person.emailAddresses || [];
    if (emails.some(e => e.value.toLowerCase() === email.toLowerCase())) {
      return item.person;
    }
  }
  return null;
}

function criarContato_(nome, email) {
  const criado = People.People.createContact({
    names: nome ? [{ givenName: nome }] : [],
    emailAddresses: [{ value: email }],
  });
  return criado.resourceName;
}

function adicionarAoGrupo_(resourceNamePessoa, resourceNameGrupo) {
  People.ContactGroups.Members.modify(
    { resourceNamesToAdd: [resourceNamePessoa] },
    resourceNameGrupo
  );
}
