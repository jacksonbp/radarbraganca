# Voz do Bairro: como está ligado

A página `site/demandas/index.html` envia cada mensagem para um "receptor" gratuito do Google,
que grava numa planilha e manda um e-mail de aviso. Esta pasta (`demandas-receptor`) não vai para o site.

## O que já existe (conta bragancaterraquerida@gmail.com)

- **Planilha "Voz do Bairro - Demandas"**, aba **Demandas**:
  https://docs.google.com/spreadsheets/d/1YAhvtB6N0D76IHdsOj2VN4-lNftJWYliRArnuShU3YA/edit
- **Receptor "Voz do Bairro - Receptor"** (Google Apps Script, projeto separado da planilha), com o código de `Codigo.gs`:
  https://script.google.com/home/projects/1WvwoX1NNg05sI193N1jdSdR_tOVVIC8WpfijdfB_ApnwFElHRZjY-bMg/edit
- Publicado como **App da Web** (Executar como: Eu; Quem pode acessar: Qualquer pessoa).
  O endereço (termina em `/exec`) está em `const ENDERECO` dentro de `site/demandas/index.html`.

Obs.: com várias contas Google abertas no Chrome, abra os links acima trocando para a conta do projeto
(o caminho "Extensões → Apps Script" de dentro da planilha falha nesse caso).

## No dia a dia

- Cada envio vira uma linha na aba **Demandas**, com protocolo em sequência (RB-0001, RB-0002…), e chega um e-mail.
- Use a coluna **Situação** (Nova, Em análise, Encaminhada, Respondida, Arquivada) para acompanhar.
- Os e-mails dos gabinetes estão no próprio Radar (ficha de cada vereador).
- Para desligar o recebimento: no Apps Script, **Implantar → Gerenciar implantações → Arquivar**.
- Se mudar o `Codigo.gs`: cole no editor, salve e faça **Implantar → Gerenciar implantações → Editar (lápis) → Nova versão**
  (assim o endereço continua o mesmo).

## Cuidados (LGPD)

- Não publique as mensagens. Só repasse nome e contato quando a coluna "Autoriza enviar nome" for **Sim**.
- Se alguém pedir para apagar a mensagem (pelo protocolo), apague a linha da planilha.

## Painel de problemas dos bairros

No projeto Apps Script que recebe as demandas, aplique a versão atualizada de
Codigo.gs e execute prepararPainelBairros uma vez. Em seguida, edite a implantação
existente, selecione Nova versão e implante. Assim o formulário conserva o endereço
já configurado. Para verificar a leitura, abra o endereço /exec da implantação
com ?painel=bairros e confira se ele retorna ok e problemas.

Na aba Problemas dos bairros, crie uma linha com o bairro, o resumo aprovado,
uma referência pública de local, a situação e a data, se houver. Marque Publicar
quando a linha estiver pronta. Desmarque para retirar do site. Edite a situação
e a data para atualizar o acompanhamento. Marque Resolvido após confirmação.
Agrupe relatos duplicados em uma única linha pública.

As colunas dessa aba são públicas quando a caixa está marcada. Mantenha
nomes, contatos, protocolos e relatos originais apenas na aba privada Demandas.
A prévia local usa exemplos fictícios. No domínio publicado, o painel consulta
o Apps Script e os dados marcados para publicação.

## Aviso no Telegram

Cada mensagem nova também chega no Telegram, com protocolo, assunto, bairro, texto e contato.
Se o mesmo assunto já chegou do mesmo bairro nos últimos 90 dias, o aviso diz quantas vezes ("🔁 Já são 3 mensagens…").
Se o Telegram falhar, nada se perde: a linha é gravada e o e-mail sai igual.

Para ligar (uma vez):
1. No Telegram, abra **@BotFather**, mande `/newbot`, escolha um nome e um usuário terminado em `bot`. Ele responde com um **token**.
2. Abra o seu robô novo no Telegram e mande **oi**.
3. No Apps Script: **Configurações do projeto (engrenagem) → Propriedades do script → Adicionar**,
   nome `TELEGRAM_TOKEN`, valor = o token. (O token nunca vai no código nem no GitHub.)
4. No editor, escolha a função **ligarTelegram** e clique em **Executar**. Autorize o acesso a "serviços externos".
   Chega no Telegram: "✅ Pronto!".
5. **Implantar → Gerenciar implantações → Editar → Nova versão → Implantar.**

Para desligar: apague a propriedade `TELEGRAM_CHAT`.

## Painel automático

Na aba **Demandas**, ao mudar a **Situação** de uma linha:
- **Em análise** → a demanda aparece no site (aba "Problemas dos bairros", Publicar marcado) com bairro, assunto e local.
- **Encaminhada** → no site vira "Encaminhado". **Respondida** → "Solução informada".
- **Arquivada** → sai do site (Publicar desmarcado).

Nome, contato, protocolo e o texto original nunca vão para o site. A atualização acontece quando alguém abre o
painel no site (no máximo 1 vez por minuto); para forçar, rode `sincronizarAgora` no editor.
O que você editar à mão na aba "Problemas dos bairros" (texto, local, "Resolvido") é respeitado até a Situação
mudar de novo na aba Demandas. Confira o **Local público**: tire número de casa se puder identificar quem reclamou.

Proteção extra: se o nome de quem mandou aparece no Bairro ou no Local (ex.: a pessoa escreveu o próprio nome
no campo Bairro), a linha é criada em "Problemas dos bairros" com **Publicar desmarcado**. Corrija e marque à mão.

## Jantar de Natal (página /natal/)

A página <https://vozdascidades.com.br/braganca/natal/> usa o mesmo receptor. Ela fica fora do menu, do sitemap e do Google
(`noindex`), para o link ser mandado só para quem comentar "AJUDA" no Instagram.

Para ligar: cole o `Codigo.gs` atualizado no editor do Apps Script, salve e faça
**Implantar → Gerenciar implantações → Editar (lápis) → Nova versão**. O endereço continua o mesmo.
Cada voluntário vira uma linha na aba **Jantar de Natal** da planilha (criada sozinha no primeiro envio) e chega um e-mail.
Antes disso, o formulário da página mostra "não foi possível enviar" (nada vai parar na aba Demandas).

Data, local e metas do jantar: abra `site/natal/index.html`, procure `CONFIG` no fim do arquivo e troque os textos.
