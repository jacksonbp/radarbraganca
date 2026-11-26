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
    if (d.formulario === 'natal') return receberNatal(d);
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
const ESTADOS_PUBLICOS = ['Publicado', 'Em análise', 'Encaminhado', 'Aguardando retorno', 'Solução informada', 'Resolvido'];

function doGet(e) {
  if (!e || !e.parameter || e.parameter.painel !== 'bairros') {
    return resposta({ ok: true, servico: 'Voz do Bairro' });
  }
  try {
    try { sincronizarPainel(); } catch (err) { console.error('Sincronizar painel: ' + err); }
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
      bairro: bairroPublico, titulo, local: localSeguro(local), situacao,
      atualizado: atualizado instanceof Date && !isNaN(atualizado.getTime())
        ? Utilities.formatDate(atualizado, 'America/Sao_Paulo', 'yyyy-MM-dd') : ''
    }];
  });
}

// ------------------------------------------------------------------ Demandas -> painel público
// Quando a Situação de uma demanda (aba Demandas) muda para Em análise, Encaminhada ou Respondida,
// cria ou atualiza a linha dela na aba pública, já com Publicar marcado. Arquivada tira do site.
// Vão para o site só: bairro, assunto e local. Nome, contato, protocolo e texto original nunca vão.
// Roda sozinho toda vez que o site abre o painel (no máximo 1 vez por minuto) e pode ser rodado pelo editor.
const PARA_PUBLICO = { 'Em análise': 'Em análise', 'Encaminhada': 'Encaminhado', 'Respondida': 'Solução informada' };

function sincronizarPainel() {
  const cache = CacheService.getScriptCache();
  if (cache.get('sinc')) return;
  cache.put('sinc', '1', 60);
  const lock = LockService.getScriptLock();
  if (!lock.tryLock(10000)) return;
  try {
    const pl = SpreadsheetApp.openById(PLANILHA_ID);
    const dem = pl.getSheetByName(ABA), pub = pl.getSheetByName(ABA_PUBLICA);
    if (!dem || !pub || dem.getLastRow() < 2) return;
    // Colunas internas da aba pública (não vão para o site): G = Protocolo, H = Situação na aba Demandas.
    if (pub.getRange(1, 7).getValue() !== 'Protocolo (interno)') {
      pub.getRange(1, 7, 1, 2).setValues([['Protocolo (interno)', 'Situação em Demandas (interno)']]).setFontWeight('bold');
    }
    pub.getRange('E2:E').setDataValidation(SpreadsheetApp.newDataValidation()
      .requireValueInList(ESTADOS_PUBLICOS, true).setAllowInvalid(false).build());

    const linhasDem = dem.getRange(2, 1, dem.getLastRow() - 1, 12).getValues();
    // getLastRow conta as caixinhas vazias; a última linha usada é a última com Bairro, Problema ou Protocolo.
    const usada = r => r[1] !== '' || r[2] !== '' || r[6] !== '';
    const tudo = pub.getLastRow() > 1 ? pub.getRange(2, 1, pub.getLastRow() - 1, 8).getValues() : [];
    let nPub = tudo.length;
    while (nPub && !usada(tudo[nPub - 1])) nPub--;
    // Se ficaram linhas vazias no meio (ex.: linhas criadas lá embaixo), sobe tudo para o começo da aba.
    const cheias = tudo.slice(0, nPub).filter(usada);
    if (cheias.length < nPub) {
      pub.getRange(2, 1, nPub, 8).clearContent();
      pub.getRange(2, 1, nPub, 1).insertCheckboxes();
      if (cheias.length) pub.getRange(2, 1, cheias.length, 8).setValues(cheias);
      nPub = cheias.length;
    }
    const linhasPub = nPub ? pub.getRange(2, 1, nPub, 8).getValues() : [];
    const onde = {};
    linhasPub.forEach((r, i) => { if (r[6]) onde[r[6]] = i; });
    const novas = [], hoje = new Date();

    linhasDem.forEach(r => {
      const protocolo = String(r[1] || ''), sit = String(r[11] || '');
      if (!protocolo) return;
      const i = onde[protocolo];
      if (i === undefined) {
        if (!PARA_PUBLICO[sit]) return;
        // Se o nome de quem mandou aparece no bairro ou no local (ex.: escreveu o próprio nome no campo Bairro),
        // a linha é criada SEM publicar, para você revisar antes.
        const bairro = limparPublico(r[4], 120), local = localSeguro(r[5]);
        const publicar = !temNome(r[8], bairro + ' ' + local);
        novas.push([publicar, bairro, limparPublico(r[3], 140), local, PARA_PUBLICO[sit], hoje, protocolo, sit]);
        return;
      }
      if (linhasPub[i][7] === sit) return; // nada mudou na aba Demandas; respeita o que foi editado à mão
      const linha = i + 2;
      if (sit === 'Arquivada') pub.getRange(linha, 1).setValue(false);
      else if (PARA_PUBLICO[sit]) pub.getRange(linha, 5, 1, 2).setValues([[PARA_PUBLICO[sit], hoje]]);
      pub.getRange(linha, 8).setValue(sit);
    });
    if (novas.length) {
      const ini = nPub + 2;
      pub.getRange(ini, 1, novas.length, 8).setValues(novas);
      pub.getRange(ini, 1, novas.length, 1).insertCheckboxes().setValues(novas.map(n => [n[0]]));
      pub.getRange(ini, 6, novas.length, 1).setNumberFormat('dd/mm/yyyy');
    }
  } finally { lock.releaseLock(); }
}

/**
 * Protege quem reclamou: tira do local o número da casa, complemento (casa, apto, bloco, lote...),
 * CEP, telefone e e-mail. Fica só a rua ou o ponto de referência. Ex.: "Rua X, 508 508" -> "Rua X".
 */
function localSeguro(x) {
  const B = '(?:^|(?<=[^A-Za-zÀ-ÿ]))', E = '(?=[^A-Za-zÀ-ÿ]|$)'; // limites de palavra que entendem acento
  let s = String(x == null ? '' : x).replace(/^'/, '');
  s = s.replace(new RegExp('[,;]?\\s*' + B + '(tel|telefone|fone|cel|celular|whats(app)?|zap|contato|cep)' + E + '[:.]?', 'gi'), ' ')
       .replace(/[\w.+-]+@[\w-]+\.[\w.]+/g, ' ')                          // e-mail
       .replace(/\(?\d{2}\)?\s*9?\d{4}[-\s]?\d{4}/g, ' ')                 // telefone
       .replace(/\d{5}-?\d{3}/g, ' ')                                     // CEP
       .replace(new RegExp(B + '(casa|apto?|apartamento|bloco|bl|lote|lt|quadra|qd|sobrado|fundos|complemento)' + E + '.*$', 'i'), ' ')
       .replace(/,\s*(n[º°o]\.?\s*)?\d.*$/i, ' ')                         // ", 508 ..." até o fim
       .replace(/\s+(n[º°o]\.?|número|numero)\s*\d.*$/i, ' ')            // "nº 508"
       .replace(/(?<!km\s*)(\s*[-–,]?\s*\d+[a-z]?)+\s*$/i, ' ');            // números soltos no fim
  return s.replace(/\s{2,}/g, ' ').replace(/[\s,;\-–]+$/, '').trim().slice(0, 160);
}

/** true se alguma palavra do nome (3+ letras, ignorando "da", "de"...) aparece no texto público. */
function temNome(nome, texto) {
  const norm = x => String(x || '').normalize('NFD').replace(/[̀-ͯ]/g, '').toLowerCase();
  const t = ' ' + norm(texto).replace(/[^a-z0-9]+/g, ' ') + ' ';
  return norm(nome).split(/[^a-z]+/).filter(p => p.length >= 3 && !['das', 'dos', 'teste'].includes(p))
    .some(p => t.includes(' ' + p + ' '));
}

function limparPublico(x, max) {
  return String(x == null ? '' : x).replace(/^'/, '').trim().slice(0, max);
}

/** Para rodar pelo editor: sincroniza agora, sem esperar o site abrir o painel. */
function sincronizarAgora() {
  CacheService.getScriptCache().remove('sinc');
  sincronizarPainel();
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

// ------------------------------------------------------------------ Jantar de Natal (página /natal/)
// Cada voluntário vira uma linha na aba "Jantar de Natal" da mesma planilha e chega um e-mail.
const ABA_NATAL = 'Jantar de Natal';
const COLUNAS_NATAL = ['Recebido em', 'Nome', 'WhatsApp', 'Bairro', 'Como quer ajudar', 'Recado', 'Situação'];

function receberNatal(d) {
  const nome = limpar(d.nome, 100), contato = limpar(d.contato, 40);
  if (nome.length < 2 || contato.replace(/\D/g, '').length < 10) return resposta({ ok: false, erro: 'dados incompletos' });
  const cache = CacheService.getScriptCache();
  const n = Number(cache.get('natal') || 0);
  if (n > 80) return resposta({ ok: false, erro: 'muitos envios, tente mais tarde' });
  cache.put('natal', String(n + 1), 3600);

  const ajuda = limpar([].concat(d.ajuda || []).join(', '), 300);
  const bairro = limpar(d.bairro, 120), recado = limpar(d.recado, 800);
  const pl = SpreadsheetApp.openById(PLANILHA_ID);
  let aba = pl.getSheetByName(ABA_NATAL);
  if (!aba) {
    aba = pl.insertSheet(ABA_NATAL);
    aba.appendRow(COLUNAS_NATAL);
    aba.setFrozenRows(1);
    aba.getRange(1, 1, 1, COLUNAS_NATAL.length).setFontWeight('bold').setBackground('#0e5a3a').setFontColor('#ffffff');
  }
  aba.appendRow([new Date(), nome, contato, bairro, ajuda, recado, 'Novo']);
  try {
    const props = PropertiesService.getScriptProperties();
    const token = props.getProperty('TELEGRAM_TOKEN'), chat = props.getProperty('TELEGRAM_CHAT');
    if (token && chat) enviarTelegram(token, chat, [
      '🎄 Jantar de Natal · novo voluntário',
      '👤 ' + nome + ' · 📱 ' + contato + (bairro ? ' · 📍 ' + bairro : ''),
      '🙌 ' + (ajuda || '-'),
      recado ? '💬 ' + recado : '',
      'Total na lista: ' + (aba.getLastRow() - 1)
    ].filter(Boolean).join('\n'));
  } catch (err) { console.warn('Telegram falhou: ' + err); }
  MailApp.sendEmail({
    to: AVISAR,
    subject: '[Jantar de Natal] Novo voluntário: ' + nome,
    body: 'Nome: ' + nome + '\nWhatsApp: ' + contato + '\nBairro: ' + (bairro || '-') +
      '\nComo quer ajudar: ' + (ajuda || '-') + '\nRecado: ' + (recado || '-') +
      '\n\nLista completa: ' + pl.getUrl()
  });
  return resposta({ ok: true });
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
    if (!token || !chat) { console.warn('Telegram: falta TELEGRAM_TOKEN ou TELEGRAM_CHAT'); return; }
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
    const r = enviarTelegram(token, chat, linhas.join(BR).slice(0, 4000));
    if (!r.ok) console.error('Telegram recusou: ' + JSON.stringify(r));
  } catch (err) { console.error('Telegram falhou: ' + err); /* aviso é extra: nunca impede a gravação */ }
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

/** Diagnóstico: mostra no registro de execução qual robô e qual conversa estão ligados (sem mostrar o token). */
function verTelegram() {
  const props = PropertiesService.getScriptProperties();
  const token = props.getProperty('TELEGRAM_TOKEN'), chat = props.getProperty('TELEGRAM_CHAT');
  const api = m => JSON.parse(UrlFetchApp.fetch('https://api.telegram.org/bot' + token + '/' + m, { muteHttpExceptions: true }).getContentText());
  const eu = api('getMe');
  Logger.log('Robô: ' + (eu.ok ? '@' + eu.result.username : 'token recusado'));
  Logger.log('Conversa guardada: ' + chat);
  if (chat) { const c = api('getChat?chat_id=' + chat); Logger.log('Essa conversa é de: ' + (c.ok ? (c.result.first_name || '') + ' ' + (c.result.last_name || '') + ' @' + (c.result.username || '-') + ' (' + c.result.type + ')' : JSON.stringify(c))); }
  const t = enviarTelegram(token, chat, '🔎 Teste de diagnóstico da Voz do Bairro');
  Logger.log('Envio de teste: ' + (t.ok ? 'aceito pelo Telegram' : JSON.stringify(t)));
}

/** Rode esta função uma vez pelo editor para criar a aba e autorizar o e-mail. */
function prepararPlanilha() {
  pegarAba();
  MailApp.sendEmail(AVISAR, '[Voz do Bairro] Teste de aviso', 'Se você recebeu este e-mail, os avisos estão funcionando.');
}
