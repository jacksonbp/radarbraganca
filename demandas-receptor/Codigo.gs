/**
 * Receptor das mensagens da página "Voz do Bairro" (site/demandas/).
 * Fica num projeto do Apps Script (script.google.com) da conta bragancaterraquerida@gmail.com
 * e grava na planilha "Voz do Bairro - Demandas" da mesma conta. Cada envio vira uma linha na aba "Demandas"
 * e manda um e-mail de aviso. Passo a passo em COMO-LIGAR.md.
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
      aba.appendRow([new Date(), v.protocolo, v.tipo, v.tema, v.bairro, v.local, v.mensagem,
        v.destino, v.nome, v.contato, v.autoriza_nome, 'Nova', '']);
    } finally { lock.releaseLock(); }

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
function doGet() { return resposta({ ok: true, servico: 'Voz do Bairro' }); }

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

/** Rode esta função uma vez pelo editor para criar a aba e autorizar o e-mail. */
function prepararPlanilha() {
  pegarAba();
  MailApp.sendEmail(AVISAR, '[Voz do Bairro] Teste de aviso', 'Se você recebeu este e-mail, os avisos estão funcionando.');
}
