/**
 * Receptor das mensagens da página "Voz do Bairro" (site/demandas/).
 * Fica num projeto do Apps Script (script.google.com) da conta bragancaterraquerida@gmail.com
 * e grava na planilha "Voz do Bairro - Demandas" da mesma conta. Cada envio vira uma linha na aba "Demandas"
 * e manda aviso por e-mail e pelo Telegram. Passo a passo em COMO-LIGAR.md.
 */

const AVISAR = 'bragancaterraquerida@gmail.com'; // quem recebe o e-mail de aviso
const PLANILHA_ID = '1YAhvtB6N0D76IHdsOj2VN4-lNftJWYliRArnuShU3YA'; // planilha "Voz do Bairro - Demandas"
const ABA = 'Demandas';
const COLUNAS = ['Recebido em', 'Protocolo', 'Tipo', 'Assunto', 'Bairro', 'Local',
  'Mensagem', 'Encaminhar para', 'Nome', 'Contato', 'Autoriza enviar nome',
  'Situação', 'Observações'];
const LIMITE = { protocolo: 40, tipo: 40, tema: 60, bairro: 120, local: 200, mensagem: 2000,
  destino: 80, nome: 100, contato: 120, autoriza_nome: 5 };

function doPost(e) {
  try {
    const d = JSON.parse((e && e.postData && e.postData.contents) || '{}');
    if (d.site_web) return resposta({ ok: true }); // armadilha de robô
    if (!d.mensagem || String(d.mensagem).trim().length < 15) return resposta({ ok: false, erro: 'mensagem curta' });

    // Limite simples contra enxurrada: no máximo 60 envios por hora no total.
    const cache = CacheService.getScriptCache();
    const n = Number(cache.get('n') || 0);
    if (n > 60) return resposta({ ok: false, erro: 'muitos envios, tente mais tarde' });
    cache.put('n', String(n + 1), 3600);

    const v = {};
    Object.keys(LIMITE).forEach(k => { v[k] = limpar(d[k], LIMITE[k]); });

    const lock = LockService.getScriptLock();
    lock.waitLock(20000);
    try {
      // Protocolo em sequência (RB-0001, RB-0002...). O contador nunca volta, mesmo se uma linha for apagada.
      const props = PropertiesService.getScriptProperties();
      const num = Number(props.getProperty('contador') || 0) + 1;
      props.setProperty('contador', String(num));
      v.protocolo = 'RB-' + String(num).padStart(4, '0');
      const aba = pegarAba();
      v.repetidas = contarParecidas(aba, v.bairro, v.tema);
      aba.appendRow([new Date(), v.protocolo, v.tipo, v.tema, v.bairro, v.local, v.mensagem,
        v.destino, v.nome, v.contato, v.autoriza_nome, 'Nova', '']);
    } finally { lock.releaseLock(); }

    avisarTelegram(v);
    MailApp.sendEmail({
      to: AVISAR,
      subject: '[Voz do Bairro] ' + v.tipo + ' – ' + v.tema + ' – ' + v.bairro,
      body: 'Nova mensagem recebida pelo site.\n\n' +
        'Protocolo: ' + v.protocolo + '\n' +
        'Tipo: ' + v.tipo + '\nAssunto: ' + v.tema + '\n' +
        'Bairro: ' + v.bairro + (v.local ? '\nLocal: ' + v.local : '') + '\n' +
        'Encaminhar para: ' + v.destino + '\n\n' +
        'Mensagem:\n' + v.mensagem + '\n\n' +
        'Nome: ' + (v.nome || '(não informado)') + '\n' +
        'Contato: ' + (v.contato || '(não informado)') + '\n' +
        'Autoriza enviar nome ao vereador: ' + v.autoriza_nome + '\n\n' +
        'Todas as mensagens ficam na planilha: ' + SpreadsheetApp.openById(PLANILHA_ID).getUrl()
    });
    return resposta({ ok: true, protocolo: v.protocolo });
  } catch (err) {
    return resposta({ ok: false, erro: 'erro interno' });
  }
}

// Abrir o endereço no navegador mostra só isto (serve para testar se está no ar).
const ABA_PUBLICA = 'Problemas dos bairros';
const CAMPOS_PUBLICOS = ['Publicar', 'Bairro', 'Problema', 'Local público', 'Situação', 'Atualizado em'];
const ESTADOS_PUBLICOS = ['Publicado', 'Encaminhado', 'Aguardando retorno', 'Solução informada', 'Resolvido'];

function doGet(e) {
  if (!e || !e.parameter || e.parameter.painel !== 'bairros') {
    return resposta({ ok: true, servico: 'Voz do Bairro' });
  }
  try {
    const aba = SpreadsheetApp.openById(PLANILHA_ID).getSheetByName(ABA_PUBLICA);
    if (!aba) return resposta({ ok: false });
    const [cabecalho, ...linhas] = aba.getDataRange().getValues();
    if (!CAMPOS_PUBLICOS.every((nome, i) => cabecalho[i] === nome)) return resposta({ ok: false });
    return resposta({ ok: true, problemas: problemasPublicos(linhas) });
  } catch (_) {
    return resposta({ ok: false });
  }
}

function problemasPublicos(linhas) {
  return linhas.flatMap(([publicar, bairro, problema, local, situacao, atualizado]) => {
    if (publicar !== true || !ESTADOS_PUBLICOS.includes(situacao)) return [];
    const titulo = String(problema || '').trim().slice(0, 140);
    const bairroPublico = String(bairro || '').trim().slice(0, 120);
    if (!titulo || !bairroPublico) return [];
    return [{
      bairro: bairroPublico, titulo, local: String(local || '').trim().slice(0, 160), situacao,
      atualizado: atualizado instanceof Date && !isNaN(atualizado.getTime())
        ? Utilities.formatDate(atualizado, 'America/Sao_Paulo', 'yyyy-MM-dd') : ''
    }];
  });
}

function prepararPainelBairros() {
  const planilha = SpreadsheetApp.openById(PLANILHA_ID);
  if (planilha.getSheetByName(ABA_PUBLICA)) return;
  const aba = planilha.insertSheet(ABA_PUBLICA);
  aba.getRange(1, 1, 1, CAMPOS_PUBLICOS.length).setValues([CAMPOS_PUBLICOS]).setFontWeight('bold');
  aba.setFrozenRows(1);
  aba.getRange('A2:A').insertCheckboxes();
  const estados = SpreadsheetApp.newDataValidation().requireValueInList(ESTADOS_PUBLICOS, true)
    .setAllowInvalid(false).build();
  aba.getRange('E2:E').setDataValidation(estados);
  aba.getRange('F2:F').setNumberFormat('dd/mm/yyyy');
}

function limpar(x, max) {
  let s = String(x == null ? '' : x).replace(/[\u0000-\u0008\u000B\u000C\u000E-\u001F]/g, '').trim().slice(0, max);
  // Impede que um texto começando com = + - @ vire fórmula na planilha.
  if (/^[=+\-@]/.test(s)) s = "'" + s;
  return s;
}

function pegarAba() {
  const pl = SpreadsheetApp.openById(PLANILHA_ID);
  let aba = pl.getSheetByName(ABA);
  if (!aba) {
    aba = pl.insertSheet(ABA);
    aba.appendRow(COLUNAS);
    aba.setFrozenRows(1);
    aba.getRange(1, 1, 1, COLUNAS.length).setFontWeight('bold').setBackground('#111a24').setFontColor('#ffffff');
    aba.setColumnWidth(7, 420);
    const regra = SpreadsheetApp.newDataValidation()
      .requireValueInList(['Nova', 'Em análise', 'Encaminhada', 'Respondida', 'Arquivada'], true).build();
    aba.getRange('L2:L').setDataValidation(regra);
  }
  return aba;
}

function resposta(obj) {
  return ContentService.createTextOutput(JSON.stringify(obj)).setMimeType(ContentService.MimeType.JSON);
}

// ------------------------------------------------------------------ Telegram
// O token do robô fica nas Propriedades do script (Configurações do projeto → Propriedades do script),
// com o nome TELEGRAM_TOKEN. Ele nunca vai para o código nem para o GitHub.

/** Avisa no Telegram. Se o Telegram falhar, a mensagem continua gravada na planilha e o e-mail sai igual. */
function avisarTelegram(v) {
  try {
    const props = PropertiesService.getScriptProperties();
    const token = props.getProperty('TELEGRAM_TOKEN'), chat = props.getProperty('TELEGRAM_CHAT');
    if (!token || !chat) return;
    const linhas = [
      '📣 Voz do Bairro · ' + v.protocolo,
      v.tipo + ' · ' + v.tema,
      '📍 ' + v.bairro + (v.local ? ' · ' + v.local : ''),
      v.repetidas ? '🔁 Já são ' + (v.repetidas + 1) + ' mensagens sobre "' + v.tema + '" neste bairro nos últimos 90 dias' : '',
      '',
      v.mensagem,
      '',
      'Encaminhar para: ' + (v.destino || '–'),
      '👤 ' + (v.nome || 'sem nome') + (v.contato ? ' · ' + v.contato : '') +
        (v.autoriza_nome === 'Sim' ? ' (autoriza enviar o nome)' : ' (NÃO autoriza enviar o nome)'),
      '',
      'Planilha: ' + SpreadsheetApp.openById(PLANILHA_ID).getUrl()
    ].filter((x, i, a) => x !== '' || (a[i - 1] !== '' && i > 0));
    enviarTelegram(token, chat, linhas.join(BR).slice(0, 4000));
  } catch (_) { /* aviso é extra: nunca impede a gravação */ }
}

const BR = String.fromCharCode(10);

function enviarTelegram(token, chat, texto) {
  const r = UrlFetchApp.fetch('https://api.telegram.org/bot' + token + '/sendMessage', {
    method: 'post', contentType: 'application/json', muteHttpExceptions: true,
    payload: JSON.stringify({ chat_id: chat, text: texto, disable_web_page_preview: true })
  });
  return JSON.parse(r.getContentText());
}

/** Conta mensagens anteriores do mesmo bairro e assunto nos últimos 90 dias (para avisar repetição). */
function contarParecidas(aba, bairro, tema) {
  const n = aba.getLastRow() - 1;
  if (n < 1 || !bairro || !tema) return 0;
  const norm = x => String(x || '').normalize('NFD').replace(/[\u0300-\u036f]/g, '').toLowerCase().trim();
  const b = norm(bairro), t = norm(tema), desde = Date.now() - 90 * 864e5;
  return aba.getRange(2, 1, n, 5).getValues()
    .filter(r => r[0] instanceof Date && r[0].getTime() >= desde && norm(r[4]) === b && norm(r[3]) === t).length;
}

/**
 * Rode esta função uma vez pelo editor, DEPOIS de mandar qualquer mensagem (ex.: "oi") para o seu robô no Telegram.
 * Ela descobre o seu chat, guarda e manda uma mensagem de teste.
 */
function ligarTelegram() {
  const props = PropertiesService.getScriptProperties();
  const token = props.getProperty('TELEGRAM_TOKEN');
  if (!token) throw new Error('Falta a propriedade TELEGRAM_TOKEN (Configurações do projeto → Propriedades do script).');
  const r = JSON.parse(UrlFetchApp.fetch('https://api.telegram.org/bot' + token + '/getUpdates', { muteHttpExceptions: true }).getContentText());
  if (!r.ok) throw new Error('O Telegram recusou o token. Confira se copiou inteiro do BotFather.');
  const ultimas = (r.result || []).map(u => u.message || u.channel_post).filter(Boolean);
  if (!ultimas.length) throw new Error('Mande "oi" para o seu robô no Telegram e rode de novo.');
  const chat = String(ultimas[ultimas.length - 1].chat.id);
  props.setProperty('TELEGRAM_CHAT', chat);
  const t = enviarTelegram(token, chat, '✅ Pronto! A partir de agora cada mensagem da Voz do Bairro chega aqui.');
  Logger.log(t.ok ? 'Telegram ligado.' : 'Falhou: ' + JSON.stringify(t));
}

/** Rode esta função uma vez pelo editor para criar a aba e autorizar o e-mail. */
function prepararPlanilha() {
  pegarAba();
  MailApp.sendEmail(AVISAR, '[Voz do Bairro] Teste de aviso', 'Se você recebeu este e-mail, os avisos estão funcionando.');
}
