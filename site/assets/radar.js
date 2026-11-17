/* Radar Bragança: código comum a todas as páginas. Os dados vêm de /dados.js (window.RB). */
(function(){
/* ============ CONFIGURAÇÃO ============ */
const CONFIG={
  cidade:'Bragança Paulista',
  contato:'contato@bragancaterraquerida.com.br',
  site:'https://www.bragancaterraquerida.com.br/'
};
/* ===================================== */
const D=window.RB, V=D.v, IT=D.items; // item: [id,codigo,texto,aaaammdd,grupo,resultado,autores,grupoSiscam,tema,rua,bairro]
const SISCAM='https://braganca.siscam.com.br';
const nf=n=>Number(n).toLocaleString('pt-BR');
const MES=['jan','fev','mar','abr','mai','jun','jul','ago','set','out','nov','dez'];
const dt=s=>{s=String(s).replace(/-/g,'');return `${+s.slice(6,8)} ${MES[+s.slice(4,6)-1]} ${s.slice(0,4)}`};
const mesAno=s=>`${MES[+s.slice(4,6)-1]} ${s.slice(0,4)}`;
const esc=s=>String(s??'').replace(/[&<>"]/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]));
const norm=s=>String(s).normalize('NFD').replace(/[̀-ͯ]/g,'').toLowerCase();
const $=id=>document.getElementById(id);
const brl=new Intl.NumberFormat('pt-BR',{style:'currency',currency:'BRL'});
const reduce=matchMedia('(prefers-reduced-motion:reduce)').matches;
const CEL=!matchMedia('(min-width:760px)').matches;
const slug=s=>norm(s).replace(/[^a-z0-9]+/g,'-').replace(/^-|-$/g,'');
const urlV=v=>`/vereador/${slug(v.ap)}/`;
const svg=(p,s=22)=>`<svg width="${s}" height="${s}" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">${p}</svg>`;
const ICON={
 pin:'<path d="M12 21s7-6.2 7-11a7 7 0 10-14 0c0 4.8 7 11 7 11z"/><circle cx="12" cy="10" r="2.5"/>',
 ask:'<path d="M21 12a8 8 0 01-11.8 7L4 20l1.2-4.4A8 8 0 1121 12z"/><path d="M9.8 9.5a2.3 2.3 0 114 1.6c-.7.6-1.3 1-1.3 1.9"/><path d="M12.5 16h.01"/>',
 medal:'<circle cx="12" cy="14" r="5"/><path d="M9 9.5L6.5 3h4L12 6.5 13.5 3h4L15 9.5"/>',
 law:'<path d="M7 3h8l4 4v14H7z"/><path d="M15 3v4h4M10 12h6M10 16h6"/>',
 dots:'<circle cx="6" cy="12" r="1.4"/><circle cx="12" cy="12" r="1.4"/><circle cx="18" cy="12" r="1.4"/>',
 road:'<path d="M8 3L4 21M16 3l4 18M12 4v3M12 11v3M12 18v3"/>',
 leaf:'<path d="M5 19c0-9 5-14 15-14 0 10-5 15-14 14z"/><path d="M5 19c3-4 6-7 10-9"/>',
 bulb:'<path d="M9 18h6M10 21h4"/><path d="M12 3a6 6 0 00-3.5 10.9c.6.5 1 1.2 1 2.1h5c0-.9.4-1.6 1-2.1A6 6 0 0012 3z"/>',
 sign:'<path d="M12 3l9 16H3z"/><path d="M12 10v4M12 17h.01"/>',
 walk:'<path d="M4 20h16M6 20v-5h4v5M10 15V9h4v11M14 9V4h4v16"/>',
 tree:'<path d="M12 21v-7"/><path d="M12 14a5 5 0 01-4-8 4.5 4.5 0 018 0 5 5 0 01-4 8z"/><path d="M6 21h12"/>',
 cross:'<path d="M9 3h6v6h6v6h-6v6H9v-6H3V9h6z"/>',
 book:'<path d="M4 5a2 2 0 012-2h13v16H6a2 2 0 00-2 2z"/><path d="M4 21V5M9 7h6"/>',
 shield:'<path d="M12 3l8 3v6c0 5-3.5 8-8 9-4.5-1-8-4-8-9V6z"/>',
 drop:'<path d="M12 3s6 6.5 6 11a6 6 0 01-12 0c0-4.5 6-11 6-11z"/>',
 bus:'<rect x="4" y="4" width="16" height="13" rx="2"/><path d="M4 11h16M8 17v3M16 17v3M8 14h.01M16 14h.01"/>',
 heart:'<path d="M12 20s-7-4.5-7-10a4 4 0 017-2.6A4 4 0 0119 10c0 5.5-7 10-7 10z"/>',
 star:'<path d="M12 3l2.7 5.6 6.1.8-4.5 4.2 1.2 6-5.5-3-5.5 3 1.2-6L3.2 9.4l6.1-.8z"/>',
 cal:'<rect x="4" y="5" width="16" height="15" rx="2"/><path d="M4 10h16M8 3v4M16 3v4"/>',
 flag:'<path d="M5 21V4M5 4h11l-2 4 2 4H5"/>',
 users:'<circle cx="9" cy="8" r="3.5"/><path d="M2.5 20a6.5 6.5 0 0113 0M16 4.5a3.5 3.5 0 010 7M18 14a6 6 0 013.5 6"/>',
 info:'<circle cx="12" cy="12" r="9"/><path d="M12 11v6M12 7.5h.01"/>',
 mega:'<path d="M3 11v3a1 1 0 001 1h2l5 4V6L6 10H4a1 1 0 00-1 1z"/><path d="M15 9a4 4 0 010 6M18 6a8 8 0 010 12"/>'
};
const CAT={
 b:['Pedidos de melhoria nos bairros','Tapar buraco, podar árvore, trocar lâmpada, limpar terreno. É um pedido: a Prefeitura decide se faz.','pin','Pedido'],
 c:['Perguntas e cobranças','Pedidos de explicação à Prefeitura e requerimentos a outros órgãos.','ask','Cobrança'],
 h:['Homenagens','Parabéns, votos de pesar, título de cidadão, medalhas, nome de rua e datas comemorativas.','medal','Homenagem'],
 l:['Propostas de lei','Projetos que criam regra, programa ou obrigação na cidade.','law','Proposta de lei'],
 o:['Outros','Moções de apoio ou repúdio e regras internas da Câmara.','dots','Outro']};
const ORDER=['b','c','h','l','o'];
const TH={luz:['Iluminação','bulb'],asf:['Asfalto e buracos','road'],tra:['Trânsito','sign'],agu:['Água e esgoto','drop'],lim:['Limpeza e poda','leaf'],cal:['Calçadas','walk'],
 laz:['Praças e lazer','tree'],sau:['Saúde','cross'],edu:['Escolas','book'],seg:['Segurança','shield'],bus:['Ônibus','bus'],
 pes:['Votos de pesar','heart'],tit:['Títulos e medalhas','star'],nom:['Nomes de rua e prédio','flag'],dat:['Datas comemorativas','cal'],par:['Parabéns e aplausos','medal']};
const TEMA={luz:'iluminação',asf:'conserto de asfalto',tra:'melhoria no trânsito',agu:'água, esgoto e drenagem',lim:'limpeza e poda',cal:'conserto de calçada',laz:'melhoria em praça e área de lazer',sau:'melhoria na saúde',edu:'melhoria em escola',seg:'segurança',bus:'melhoria no ônibus'};

function clean(it){
  let t=it[2].trim();
  t=t.replace(/^(solicitando|solicita|requer(?:endo)?|indicando|indica)\s+(?:ao\s+(?:poder\s+)?executivo(?:\s+municipal)?\s*,?\s*)?(?:a\s+|o\s+)?/i,'');
  return t.charAt(0).toUpperCase()+t.slice(1);
}
IT.forEach(it=>{it.n=norm(it[2]+' '+it[9]+' '+it[10]);it.tx=clean(it)});
const hue=i=>(i*47+200)%360;
V.forEach((v,i)=>{const w=v.ap.split(/\s+/).filter(x=>!/^(da|de|do|dos|das)$/i.test(x));v.in=(w[0][0]+(w.length>1?w[w.length-1][0]:'')).toUpperCase();v.i=i;v.tot=ORDER.reduce((s,c)=>s+v.cat[c],0)});
const foto=(v,cls='av')=>v.foto?`<img class="${cls}" src="/fotos/${v.id}.jpg" alt="" loading="lazy">`:`<span class="${cls} ph0" style="background:hsl(${hue(v.i)} 80% 92%);color:hsl(${hue(v.i)} 55% 28%);display:grid;place-items:center;font-weight:700" aria-hidden="true">${v.in}</span>`;
const av=i=>foto(V[i]);
D.rep.forEach(g=>{g.items=g.ids.map(n=>IT[n])});
/* contagem pelo tipo oficial da Câmara (inclui coautoria, como a busca da Câmara por autor) */
const TIPOS=[['ind','Indicações','indicação',/^Indica/,'pedidos à Prefeitura'],['ped','Pedidos de informação','pedido de informação',/^Pedido de Informa/,'perguntas oficiais à Prefeitura'],
 ['req','Requerimentos','requerimento',/^Requerimento/,'pedidos a outros órgãos e à Câmara'],['moc','Moções','moção',/^Mo/,'apoio, repúdio ou homenagem'],
 ['pl','Projetos de lei','projeto de lei',/^Projeto de Lei/,'inclui lei complementar'],['pr','Outros projetos','outro projeto',/^Projeto/,'resolução e decreto legislativo']];
V.forEach(v=>{v.tp={};TIPOS.forEach(t=>v.tp[t[0]]=0)});
IT.forEach(it=>{const t=TIPOS.find(t=>t[3].test(it[1]));if(t)it[6].forEach(i=>V[i].tp[t[0]]++)});
const pctPres=v=>{const t=v.P+v.A+v.F;return t?Math.round(v.P/t*100):null};

/* ---------- cartão de proposta ---------- */
function stt(r){if(!r)return'';const k=/^aprovad/i.test(r)?'ok':/rejeit|vetad/i.test(r)?'no':'';return `<span class="stt ${k}">${esc(r)}</span>`}
function itemHTML(it,showAut){
  const c=it[4], t=TH[it[8]], icon=t?t[1]:CAT[c][2];
  const who=showAut?`<span class="who">${it[6].slice(0,3).map(a=>`<a href="${urlV(V[a])}" style="display:contents;color:inherit;text-decoration:none">${av(a)}<span class="n">${esc(V[a].ap)}</span></a>`).join('')}${it[6].length>3?`<span>+${it[6].length-3}</span>`:''}</span>`:'<span></span>';
  return `<li class="it k-${c}"><span class="ic">${svg(ICON[icon])}</span><div>
    <p class="tx">${esc(it.tx)}</p>
    <div class="mt"><span class="lab">${t?esc(t[0]):CAT[c][3]}</span>${stt(it[5])}<span>${dt(it[3])}</span><span>·</span><span>${esc(it[1])}</span></div>
    <div class="ft">${who}<a class="ext" href="${SISCAM}/Documentos/Details?id=${it[0]}" target="_blank" rel="noopener">Abrir na Câmara ↗</a></div></div></li>`;
}
function pager(host,items,showAut,step){
  let n=0; host.innerHTML='<ul class="items"></ul>';
  const ul=host.firstChild, btn=document.createElement('button');
  btn.className='more'; btn.type='button';
  const add=()=>{ul.insertAdjacentHTML('beforeend',items.slice(n,n+step).map(i=>itemHTML(i,showAut)).join(''));n+=step;
    if(n>=items.length)btn.remove();else btn.textContent=`Mostrar mais ${Math.min(step,items.length-n)} de ${nf(items.length-n)}`};
  btn.addEventListener('click',add); if(items.length>step)host.appendChild(btn); add();
  if(!items.length)host.innerHTML='<p class="mute">Nada por aqui ainda.</p>';
}
function themeCount(items){const m=new Map();items.forEach(it=>{if(it[8])m.set(it[8],(m.get(it[8])||0)+1)});return [...m.entries()].sort((a,b)=>b[1]-a[1])}

/* ---------- painel lateral (criado em toda página) ---------- */
document.body.insertAdjacentHTML('beforeend',`<div class="veil" id="veil"></div>
<aside class="sheet" id="sheet" role="dialog" aria-modal="true" aria-labelledby="sh-t">
  <div class="sh-top" id="sh-top"><span class="ci" id="sh-i"></span><div><h2 id="sh-t"></h2><p id="sh-s"></p></div><button class="x" id="sh-x" type="button" aria-label="Fechar">×</button></div>
  <div id="sh-f"></div><div id="sh-b"></div></aside>`);
const sheet=$('sheet'), veil=$('veil'); let lastFocus=null;
function openSheet(k,icon,title,sub){
  lastFocus=document.activeElement; $('sh-top').className='sh-top k-'+k; $('sh-i').innerHTML=svg(ICON[icon],24);
  $('sh-t').textContent=title; $('sh-s').textContent=sub||''; $('sh-f').innerHTML=''; $('sh-f').style.display='none'; $('sh-b').innerHTML=''; $('sh-b').scrollTop=0;
  sheet.classList.add('on'); veil.classList.add('on'); document.body.style.overflow='hidden'; $('sh-x').focus();
}
function closeSheet(){sheet.classList.remove('on');veil.classList.remove('on');document.body.style.overflow='';if(lastFocus)lastFocus.focus()}
$('sh-x').addEventListener('click',closeSheet); veil.addEventListener('click',closeSheet);
document.addEventListener('keydown',e=>{if(e.key==='Escape'&&sheet.classList.contains('on'))closeSheet()});
function openCat(c,vi){
  const all=IT.filter(it=>it[4]===c&&(vi==null||it[6].includes(vi)));
  openSheet(c,CAT[c][2],CAT[c][0],`${nf(all.length)} ${vi==null?'de todos os vereadores':'de '+V[vi].ap} até agora`);
  const th=themeCount(all); let cur='';
  const draw=()=>pager($('sh-b'),cur?all.filter(it=>it[8]===cur):all,vi==null,20);
  if(th.length>1){
    $('sh-f').style.display='';
    $('sh-f').innerHTML=`<ul class="chips"><li><button class="chip on" type="button" data-t="">Tudo<small>${nf(all.length)}</small></button></li>${th.map(([k,n])=>`<li><button class="chip" type="button" data-t="${k}">${esc(TH[k][0])}<small>${nf(n)}</small></button></li>`).join('')}</ul>`;
    $('sh-f').onclick=e=>{const b=e.target.closest('[data-t]');if(!b)return;cur=b.dataset.t;$('sh-f').querySelectorAll('.chip').forEach(x=>x.classList.toggle('on',x===b));$('sh-b').scrollTop=0;draw()};
  }
  draw();
}
const naosHTML=v=>'<ul class="items">'+v.naos.slice().sort((a,b)=>b.d.localeCompare(a.d)).map(n=>`<li class="it k-o"><span class="ic">${svg(ICON.sign)}</span><div><p class="tx">${esc(n.e)}</p>
    <div class="mt"><span class="stt ${n.v==='nao'?'no':''}">${n.v==='nao'?'Votou não':'Absteve-se'}</span><span>${dt(n.d)}</span><span>·</span><span>${esc(n.t)}</span></div>
    <div class="ft"><span>${n.a?'Proposta de: '+esc(n.a):''}</span><a class="ext" href="${esc(n.u)}" target="_blank" rel="noopener">Abrir na Câmara ↗</a></div></div></li>`).join('')+'</ul>';
function openNaos(vi){const v=V[vi];openSheet('o','sign',`Quando ${v.ap} não votou “sim”`,`${v.naos.length} ${v.naos.length===1?'votação':'votações'} até agora`);$('sh-b').innerHTML=naosHTML(v)}
const AVISO_VG=`<p class="warn" style="margin-bottom:14px">O valor é o que a Câmara registrou na prestação de contas de cada viagem: alimentação e hospedagem de <b>todos os participantes</b> (inclusive motorista e servidores). <b>Não inclui combustível e pedágio.</b></p>`;
const vgHTML=v=>'<ul class="items">'+(v.vg||[]).map(t=>`<li class="it k-o"><span class="ic">${svg(ICON.bus)}</span><div><p class="tx"><b>${esc(t.de)}</b><br>${esc(t.mo)}</p>
    <div class="mt">${t.v!=null?`<span class="stt">${brl.format(t.v)}</span>`:'<span class="stt">valor não lido</span>'}${t.dt?`<span>${esc(t.dt)}</span>`:''}<span>·</span><span>Despesa ${esc(t.k.split('-')[1])}/${esc(t.k.split('-')[0])}</span></div>
    <div class="ft"><span></span>${t.u?`<a class="ext" href="${esc(t.u)}" target="_blank" rel="noopener">Prestação de contas ↗</a>`:''}</div></div></li>`).join('')+'</ul>';
function openVg(vi){const v=V[vi];openSheet('o','bus',`Viagens oficiais de ${v.ap}`,`${v.vg.length} ${v.vg.length===1?'viagem':'viagens'} · ${brl.format(v.vgt||0)} desde a posse`);$('sh-b').innerHTML=AVISO_VG+vgHTML(v)}

/* ---------- pedidos repetidos + cobrar ---------- */
const repHTML=g=>`<button class="rp" type="button" data-g="${D.rep.indexOf(g)}"><span class="rn num">${g.n}<small>VEZES</small></span>
  <span class="rr">${esc(g.r)}</span><span class="rb">${esc(g.b||CONFIG.cidade)}</span>
  <span class="rm"><span class="lab">${esc(TH[g.th][0])}</span><span>${g.a} ${g.a===1?'vereador pediu':'vereadores pediram'}</span><span>·</span><span>de ${mesAno(g.d0)} a ${mesAno(g.d1)}</span></span><span class="go">Ver pedidos e cobrar →</span></button>`;
const SITE=/^https?:/.test(location.protocol)&&!/claude|localhost|127\./.test(location.hostname)?location.origin+'/':CONFIG.site;
function openRep(g){
  openSheet('b',TH[g.th][1],g.r,`${TH[g.th][0]} · pedido ${g.n} vezes até agora${g.b?' · '+g.b:''}`);
  const cnt=new Map(); g.items.forEach(it=>it[6].forEach(a=>cnt.set(a,(cnt.get(a)||0)+1)));
  const who=[...cnt.entries()].sort((a,b)=>b[1]-a[1]);
  const msg=a=>`Olá, ${V[a].ap}. Moro em ${CONFIG.cidade}. A Câmara já recebeu ${g.n} pedidos de ${TEMA[g.th]||'melhoria'} na ${g.r}${g.b?', '+g.b:''}, desde ${mesAno(g.d0)}. ${cnt.get(a)===1?'Um deles saiu':cnt.get(a)+' deles saíram'} do seu gabinete, e o problema continua. O que a Prefeitura respondeu? O que ainda dá para fazer?\n\nFonte: ${SITE}`;
  $('sh-b').innerHTML=`<div class="cob"><h3>Cobre uma resposta</h3>
    <p>A mensagem já vem pronta. Escolha o vereador, ajuste o texto se quiser e envie.</p>
    <label class="field">Para quem<select id="cob-v">${who.map(([a,n])=>`<option value="${a}">${esc(V[a].ap)} (${n} ${n===1?'pedido':'pedidos'} para esta rua)</option>`).join('')}</select></label>
    <label class="field">Mensagem<textarea id="cob-t"></textarea></label>
    <div class="acts" id="cob-a"></div><div class="ct" id="cob-c"></div></div>
    <p class="h3">Os ${g.n} pedidos, do mais recente ao mais antigo</p><div id="replist"></div>`;
  const sel=$('cob-v'), ta=$('cob-t');
  const links=()=>{const v=V[+sel.value], t=encodeURIComponent(ta.value);
    $('cob-a').innerHTML=(v.email?`<a class="btn" href="mailto:${esc(v.email)}?subject=${encodeURIComponent(g.r+': o problema continua')}&body=${t}">Enviar por e-mail</a>`:'')
      +`<a class="btn wa" href="https://wa.me/?text=${t}" target="_blank" rel="noopener">Mandar no grupo do bairro</a><button class="btn gh" type="button" id="cob-cp">Copiar mensagem</button>`;
    $('cob-c').innerHTML=(v.email?`E-mail oficial do gabinete: <b>${esc(v.email)}</b> · `:'')+'Telefone da Câmara: <b>(11) 4892-6200</b>';
    $('cob-cp').onclick=async e=>{try{await navigator.clipboard.writeText(ta.value);e.target.textContent='Copiado'}catch(_){ta.focus();ta.select();e.target.textContent='Selecionado: copie com o dedo'}}};
  const fill=()=>{ta.value=msg(+sel.value);links()};
  sel.addEventListener('change',fill); ta.addEventListener('input',links); fill();
  pager($('replist'),g.items,true,20);
}
document.addEventListener('click',e=>{const b=e.target.closest('[data-g]');if(b)openRep(D.rep[+b.dataset.g])});
function listaReps(host,lista,passo){
  let n=0; const btn=document.createElement('button'); btn.className='more'; btn.type='button'; btn.style.gridColumn='1/-1';
  if(!lista.length){host.innerHTML='<p class="mute">Ainda não há pedidos repetidos para a mesma rua.</p>';return}
  const add=()=>{host.insertAdjacentHTML('beforeend',lista.slice(n,n+passo).map(repHTML).join(''));n+=passo;host.appendChild(btn);
    if(n>=lista.length)btn.remove();else btn.textContent=`Mostrar mais ruas (${lista.length-n} na fila)`};
  btn.addEventListener('click',()=>{btn.remove();add()}); add();
}

/* ---------- peças do vereador ---------- */
function ring(v,s=76){
  const t=v.P+v.A+v.F, r=s*.395, sw=s*.118, c=s/2;
  if(!t)return `<div class="ring"><svg width="${s}" height="${s}" viewBox="0 0 ${s} ${s}"><circle cx="${c}" cy="${c}" r="${r}" fill="none" stroke="#eef1f4" stroke-width="${sw}"/></svg><b>–</b></div>`;
  const C=2*Math.PI*r, seg=(n,col,off)=>n?`<circle cx="${c}" cy="${c}" r="${r}" fill="none" stroke="${col}" stroke-width="${sw}" stroke-dasharray="${n/t*C} ${C}" stroke-dashoffset="${-off/t*C}" transform="rotate(-90 ${c} ${c})"/>`:'';
  return `<div class="ring"><svg width="${s}" height="${s}" viewBox="0 0 ${s} ${s}" role="img" aria-label="${v.P} presenças em ${t} reuniões"><circle cx="${c}" cy="${c}" r="${r}" fill="none" stroke="#eef1f4" stroke-width="${sw}"/>${seg(v.P,'#111a24',0)}${seg(v.A,'#d99a2b',v.P)}${seg(v.F,'#cf3a2e',v.P+v.A)}</svg><b class="num">${Math.round(v.P/t*100)}%</b></div>`;
}
function comHTML(v){
  const c=v.cm; if(!c)return '';
  const t=c.P+c.A+c.F;
  if(!t)return `<div class="com"><span class="cl">Comissões</span><span class="mute">Não aparece em nenhuma lista de presença de comissão registrada no sistema.</span></div>`;
  const por=Object.entries(c.por).map(([s,x])=>`${esc((D.comissoes||{})[s]||s)}: ${x.P} de ${x.P+x.A+x.F}`).join(' · ');
  return `<div class="com num"><span class="cl">Comissões</span><span><b>${c.P} de ${t}</b> reuniões (${Math.round(c.P/t*100)}%) · <b class="${c.F?'bad':''}">${c.F} ${c.F===1?'falta':'faltas'}</b>${c.A?` · ${c.A} justificada${c.A>1?'s':''}`:''}</span><small class="mute">${por}</small></div>`;
}
const ANOS_ATUAL=Math.max(.25,(Date.now()-new Date(D.posse+'T00:00:00-03:00').getTime())/(365.25*864e5));
function antHTML(v){
  if(!v.ant)return '';
  if(!v.ant.tot)return `<p class="vg mute">Não apresentou propostas em 2021–2024: é o primeiro mandato ou era suplente.</p>`;
  const a=v.ant.tot/4, b=v.tot/ANOS_ATUAL, d=a?Math.round((b-a)/a*100):0;
  const f=x=>x.toLocaleString('pt-BR',{maximumFractionDigits:0});
  return `<div class="cmp num"><div><b>${f(a)}</b><span>propostas por ano antes</span></div><div><b>${f(b)}</b><span>propostas por ano agora</span></div><div class="${d>=0?'up':'down'}"><b>${d>0?'+':''}${d}%</b><span>${d>=0?'a mais':'a menos'}</span></div></div>
    <p class="mute" style="font-size:12.5px;margin:6px 0 0">Antes: ${nf(v.ant.cat.b)} pedidos, ${nf(v.ant.cat.l)} propostas de lei, ${nf(v.ant.cat.h)} homenagens (4 anos).</p>`;
}
const bar5=v=>`<div class="bar5" aria-hidden="true">${ORDER.map(c=>v.cat[c]?`<i class="k-${c}" style="flex:${v.cat[c]} 1 0"></i>`:'').join('')}</div>`;
function vcard(v){
  const p=pctPres(v), cm=v.cm||{P:0,A:0,F:0}, tc=cm.P+cm.A+cm.F;
  return `<a class="vcard" href="${urlV(v)}" style="--tint:hsl(${hue(v.i)} 85% 94%)">${foto(v,'')}
    <h3>${esc(v.ap)}</h3><span class="pill">${esc(v.part)}${v.mesa?' · '+esc(v.mesa):''}</span>
    <div class="kp num"><div><b>${p==null?'–':p+'%'}</b><span>presença</span></div><div><b>${tc?Math.round(cm.P/tc*100)+'%':'–'}</b><span>comissões</span></div><div><b>${nf(v.tot)}</b><span>propostas</span></div></div>
    ${bar5(v)}<span class="go">Ver tudo sobre ${esc(v.ap.split(' ')[0])} →</span></a>`;
}
const ORD={nome:(a,b)=>a.ap.localeCompare(b.ap,'pt'),faltas:(a,b)=>(b.F-a.F)||(b.A-a.A),l:(a,b)=>b.cat.l-a.cat.l,h:(a,b)=>b.cat.h-a.cat.h,b:(a,b)=>b.cat.b-a.cat.b,tot:(a,b)=>b.tot-a.tot,nao:(a,b)=>(b.vn+b.va)-(a.vn+a.va),vot:(a,b)=>(b.vot||0)-(a.vot||0),vg:(a,b)=>(b.vgt||0)-(a.vgt||0),cf:(a,b)=>((b.cm||{}).F||0)-((a.cm||{}).F||0)};

/* ---------- partes comuns ---------- */
function countUp(el,to){ if(!el)return; if(reduce){el.textContent=nf(to);return} const t0=performance.now(),from=Math.round(to*.82);
  const step=t=>{const p=Math.min(1,(t-t0)/900),e=1-Math.pow(1-p,3);el.textContent=nf(Math.round(from+(to-from)*e));if(p<1)requestAnimationFrame(step)};requestAnimationFrame(step)}
const GER=new Date(D.gerh);
function ago(){const m=Math.max(0,Math.round((Date.now()-GER.getTime())/6e4));
  return m<2?'agora mesmo':m<60?`há ${m} minutos`:m<120?'há 1 hora':m<1440?`há ${Math.floor(m/60)} horas`:m<2880?'ontem':`há ${Math.floor(m/1440)} dias`}
document.querySelectorAll('.phead>.eyebrow').forEach(el=>{el.insertAdjacentText('beforeend',` · atualizado em ${GER.toLocaleDateString('pt-BR',{day:'numeric',month:'long'})}`)});
document.querySelectorAll('[data-atualizado]').forEach(el=>{el.textContent=`Dados conferidos na Câmara em ${GER.toLocaleDateString('pt-BR',{day:'numeric',month:'long'})}, às ${GER.toLocaleTimeString('pt-BR',{hour:'2-digit',minute:'2-digit'})}.`});

/* ================= PÁGINAS ================= */
const P={};

P.inicio=function(){
  $('livet').textContent=`dados conferidos ${ago()}`; setInterval(()=>{$('livet').textContent=`dados conferidos ${ago()}`},6e4);
  const STATS=[
    ['',D.totalPropostas??IT.length,'propostas até agora',''],
    ['k-b',D.catot.b||0,'pedidos nos bairros','b'],
    ['k-h',D.catot.h||0,'homenagens','h'],
    ['k-l',D.catot.l||0,'propostas de lei','l']
  ];
  $('stats').innerHTML=STATS.map(([k,n,label,category],i)=>{
    const filter=category ? `?categoria=${category}` : '';
    return `<a class="stat ${k}" href="/propostas/${filter}#lista-propostas"><b class="num" id="st${i}">${nf(n)}</b><span>${label}</span><span class="stat-link">Ver registros &rarr;</span></a>`;
  }).join('');
  STATS.forEach(([k,n],i)=>countUp($('st'+i),n));
  const POSSE=new Date(D.posse+'T00:00:00-03:00').getTime(), POR_MS=V.length*D.sal.v*12/(365.25*864e5);
  const tick=()=>{$('tick').textContent=brl.format((Date.now()-POSSE)*POR_MS)}; tick(); if(!reduce)setInterval(tick,120);
  $('msal').textContent=`${V.length} vereadores × ${brl.format(D.sal.v)} por mês, desde ${dt(D.posse)}`+(D.sal.confirmado?'':' · valor mensal a confirmar no texto oficial');
  $('faces').innerHTML=V.slice().sort(ORD.nome).map(v=>`<li><a href="${urlV(v)}">${foto(v,'')}<span>${esc(v.ap)}</span></a></li>`).join('');
  $('pct').textContent=D.nvot?Math.round(D.unan/D.nvot*100)+'%':'–';
  {const div=D.nvot-D.unan;
  $('pctb').innerHTML=`<i class="a" style="flex:${D.unan}"></i><i class="b" style="flex:${div}"></i>`;
  $('pctl').innerHTML=`<span><i class="a"></i>${nf(D.unan)} com todos de acordo</span><span><i class="b"></i>${nf(div)} com a Câmara dividida</span>`;
  $('pctd').textContent=`São as ${nf(D.nvot)} votações desde ${dt(D.pri)} em que o sistema da Câmara registra o voto de cada vereador.`;}
  const lei0=D.catot.l||0, ped0=D.catot.b||0;
  $('rz').textContent=lei0?nf(Math.round(ped0/lei0)):'–';
  $('rzb').innerHTML=`<i class="p" style="flex:${ped0}"></i><i class="l" style="flex:${lei0}"></i>`;
  $('rzl').innerHTML=`<span><i class="p"></i>${nf(ped0)} pedidos de melhoria</span><span><i class="l"></i>${nf(lei0)} projetos de lei</span>`;
  $('rzd').textContent=`Desde a posse. Pedido de melhoria é quando o vereador pede à Prefeitura um conserto na rua ou no bairro; projeto de lei cria ou muda uma regra da cidade.`;
  $('bairros-chips').innerHTML=D.bairros.slice(0,8).map(b=>`<li><a class="chip" href="/bairros/?q=${encodeURIComponent(b)}">${esc(b)}</a></li>`).join('');
  if ($('hq-bairros')) $('hq-bairros').replaceChildren(...D.bairros.map(b => new Option(b,b)));
  $('fbq').addEventListener('submit',e=>{e.preventDefault();location.href='/bairros/?q='+encodeURIComponent($('hq').value.trim())});
  listaReps($('reps'),D.rep.slice(0,CEL?3:6),CEL?3:6);
};

P.vereadores=function(){
  const pct=D.nvot?Math.floor(D.unan/D.nvot*100):0;
  $('vsub').textContent=`Os ${V.length} vereadores da legislatura 2025–2028, com a mesma régua. Em ${pct} de cada 100 votações com voto registrado, todos votaram igual. Toque em um vereador para ver tudo o que ele fez.`;
  [...new Set(V.map(v=>v.part))].sort((a,b)=>a.localeCompare(b,'pt')).forEach(p=>{const o=document.createElement('option');o.value=p;o.textContent=`${p} (${V.filter(v=>v.part===p).length})`;$('partido').appendChild(o)});
  const render=()=>{
    const q=norm($('q').value.trim()),p=$('partido').value,o=$('ordem').value;
    const L=V.filter(v=>(!p||v.part===p)&&(!q||norm(v.ap+' '+v.nome).includes(q))).sort((a,b)=>ORD[o](a,b)||ORD.nome(a,b));
    $('grid').innerHTML=L.length?L.map(vcard).join(''):'<p class="mute">Nenhum vereador com esse nome. Apague a busca ou escolha “Todos”.</p>';
    $('conta').textContent=L.length===V.length?`Mostrando os ${V.length} vereadores.`:`Mostrando ${L.length} de ${V.length} vereadores.`;
  };
  ['q','partido','ordem'].forEach(id=>$(id).addEventListener('input',render)); render();
  const NOMES=[...V].sort(ORD.nome);
  // planilha
  $('csv').addEventListener('click',()=>{
    const C=[['Vereador',v=>v.ap],['Nome completo',v=>v.nome],['Partido',v=>v.part],['Reuniões presente',v=>v.P],['Ausências justificadas',v=>v.A],['Faltas',v=>v.F],
      ['Comissões presente',v=>(v.cm||{}).P||0],['Comissões faltas',v=>(v.cm||{}).F||0],['Propostas total',v=>v.tot],['Pedidos de melhoria no bairro',v=>v.cat.b],['Cobranças',v=>v.cat.c],
      ['Homenagens',v=>v.cat.h],['Projetos de lei',v=>v.cat.l],['Outras',v=>v.cat.o],...TIPOS.map(([k,pl])=>[pl+' (contagem da Câmara)',v=>v.tp[k]]),['Votos sim',v=>v.vs],['Votos não',v=>v.vn],['Abstenções',v=>v.va],
      ['Projetos da Prefeitura votados',v=>(v.gov||[])[1]||0],['Votou sim nesses',v=>(v.gov||[])[0]||0],['Viagens',v=>(v.vg||[]).length],['Gasto em viagens (R$)',v=>String(v.vgt||0).replace('.',',')],
      ['Votos em 2024',v=>v.vot||0],['Ficha na Câmara',v=>v.url]];
    const q=x=>{x=String(x??'');return /[;"\n]/.test(x)?'"'+x.replace(/"/g,'""')+'"':x};
    const linhas=[C.map(c=>c[0]).join(';'),...NOMES.map(v=>C.map(c=>q(c[1](v))).join(';')),'',
      q(`Fonte: Radar Bragança (bragancaterraquerida.com.br), dados oficiais da Câmara, TSE e Portal da Transparência. Desde ${new Date(D.posse+'T12:00').toLocaleDateString('pt-BR')}, atualizado em ${GER.toLocaleDateString('pt-BR')}.`)];
    const blob=new Blob(['﻿'+linhas.join('\r\n')],{type:'text/csv;charset=utf-8'});
    const u=URL.createObjectURL(blob),l=document.createElement('a');l.href=u;l.download=`radar-braganca-vereadores-${GER.toISOString().slice(0,10)}.csv`;
    document.body.appendChild(l);l.click();l.remove();setTimeout(()=>URL.revokeObjectURL(u),2000);
  });
};

P.comparar=function(){
  const NOMES=[...V].sort(ORD.nome), qs=new URLSearchParams(location.search);
  const pega=(k,d)=>V.find(v=>v.id==qs.get(k))||d;
  let a=pega('a',NOMES[0]), b=pega('b',NOMES.find(v=>v!==a));
  const pp=(x,t)=>t?Math.round(x/t*100):null;
  const pres=v=>{const t=v.P+v.A+v.F;return [pp(v.P,t),`${v.P} de ${t} reuniões`]};
  const com=v=>{const c=v.cm||{P:0,A:0,F:0},t=c.P+c.A+c.F;return [pp(c.P,t),t?`${c.P} de ${t} reuniões`:'sem lista registrada']};
  const gov=v=>v.gov&&v.gov[1]?[pp(v.gov[0],v.gov[1]),`${v.gov[0]} de ${v.gov[1]} projetos`]:[null,''];
  const G=[
    ['Presença',[['Presença nas reuniões',pres,1],['Faltas nas reuniões',v=>[v.F,''],0],['Presença nas comissões',com,1,'grupos de vereadores que analisam os projetos']]],
    ['Propostas desde a posse',[['Total de propostas',v=>[v.tot,''],0],['Pedidos de melhoria no bairro',v=>[v.cat.b,''],0,'tapar buraco, podar árvore, trocar lâmpada'],
      ['Cobranças à Prefeitura',v=>[v.cat.c,''],0,'perguntas e pedidos de explicação'],['Projetos de lei',v=>[v.cat.l,''],0,'propostas de novas regras para a cidade'],['Homenagens',v=>[v.cat.h,''],0,'parabéns, títulos, nomes de rua']]],
    ['Na contagem oficial da Câmara',TIPOS.map(([k,pl,,,ex])=>[pl,v=>[v.tp[k],''],0,ex])],
    ['Votos e gastos',[['Votou a favor dos projetos',v=>{const t=v.vs+v.vn+v.va;return [pp(v.vs,t),t?`votou contra ${nf(v.vn)} ${v.vn===1?'vez':'vezes'} em ${nf(t)} votações`:'']},1,'de cada 100 votações, em quantas votou “sim”'],['Apoio aos projetos da Prefeitura',gov,1,'votou “sim” nos projetos enviados pelo prefeito'],
      ['Viagens oficiais',v=>[(v.vg||[]).length,(v.vg||[]).length?brl.format(v.vgt||0):''],0],['Votos na eleição de 2024',v=>[v.vot||0,''],0]]]];
  const fmt=(n,pc)=>n==null?'–':pc?n+'%':nf(n);
  const card=(v,lado)=>`<div class="vs-c" style="--h:${hue(v.i)}">${v.foto?`<img src="/fotos/${v.id}.jpg" alt="Foto de ${esc(v.ap)}">`:`<span class="vs-ph">${esc(v.in)}</span>`}
    <a class="vs-n" href="${urlV(v)}">${esc(v.ap)}</a><span class="pill">${esc(v.part)}${v.mesa?' · '+esc(v.mesa):''}</span>
    <label class="vs-s"><span class="sr">Trocar vereador</span><select data-l="${lado}">${NOMES.map(x=>`<option value="${x.id}"${x===v?' selected':''}>${esc(x.ap)}</option>`).join('')}</select></label></div>`;
  const desenha=foco=>{
    $('vs').innerHTML=card(a,'a')+'<span class="vs-x" aria-hidden="true">×</span>'+card(b,'b');
    const j=(a.jt||[]).find(x=>x[0]===b.id);
    $('cmp').style.cssText=`--ha:${hue(a.i)};--hb:${hue(b.i)}`;
    const hd=`<div class="cg-hd" aria-hidden="true"><span class="a">${esc(a.ap)}</span><span class="b">${esc(b.ap)}</span></div>`;
    $('cmp').innerHTML=G.map(([tit,L])=>`<div class="cg"><h2>${tit}</h2>${hd}${L.map(([n,f,pc,ex])=>{
      const [x,dx]=f(a), [y,dy]=f(b), max=pc?100:Math.max(1,x||0,y||0);
      const w=n=>n==null?0:Math.max(2,Math.round(n/max*100));
      return `<div class="cr"><div class="cr-l">${n}${ex?`<small>${ex}</small>`:''}</div>
        <div class="cr-v a"><b class="num">${fmt(x,pc)}</b><small>${dx}</small><i style="--w:${w(x)}%"></i></div>
        <div class="cr-v b"><b class="num">${fmt(y,pc)}</b><small>${dy}</small><i style="--w:${w(y)}%"></i></div></div>`}).join('')}</div>`).join('')
      +(a===b?'':`<div class="cg cg-j"><h2>Os dois votam juntos?</h2><p>${j?`<b class="num">${j[1]}%</b> Nas ${j[2]} votações em que a Câmara se dividiu e os dois votaram, eles votaram igual em ${j[1]} de cada 100.`:'Os dois votaram juntos em poucas votações divididas, então não dá para comparar.'}</p></div>`);
    $('vs').querySelectorAll('select').forEach(s=>s.addEventListener('change',()=>{const v=V.find(x=>x.id==s.value);if(s.dataset.l==='a')a=v;else b=v;
      history.replaceState(null,'',`?a=${a.id}&b=${b.id}`);desenha(s.dataset.l)}));
    if(foco)$('vs').querySelector(`select[data-l="${foco}"]`).focus();
  };
  const copy=$('cmp-copy');
  if(copy) copy.addEventListener('click',async()=>{
    const url=new URL('comparar/',SITE);
    url.searchParams.set('a',a.id);
    url.searchParams.set('b',b.id);
    const status=$('cmp-copy-status');
    try{
      await navigator.clipboard.writeText(url.href);
      status.textContent='Link copiado.';
    }catch(_){
      const link=document.createElement('a');
      link.href=url.href;
      link.textContent=url.href;
      status.replaceChildren(link);
    }
  });
  desenha();
};

P.prefeitura=function(){
  const F=window.PF; if(!F)return;
  const MES=['jan','fev','mar','abr','mai','jun','jul','ago','set','out','nov','dez'];
  const MESX=['janeiro','fevereiro','março','abril','maio','junho','julho','agosto','setembro','outubro','novembro','dezembro'];
  const mi=v=>{const a=Math.abs(v);return a>=1e9?(v/1e9).toLocaleString('pt-BR',{maximumFractionDigits:2})+' bi':a>=1e6?(v/1e6).toLocaleString('pt-BR',{maximumFractionDigits:1})+' mi':a>=1e3?Math.round(v/1e3).toLocaleString('pt-BR')+' mil':nf(v)};
  const R=v=>'R$ '+mi(v);
  const cnpj=d=>d.length===14?`${d.slice(0,2)}.${d.slice(2,5)}.${d.slice(5,8)}/${d.slice(8,12)}-${d.slice(12)}`:d;
  const anos=Object.keys(F.anos).sort(); let ano=anos[anos.length-1];
  const ate=a=>{const L=F.meses.filter(m=>m[0].startsWith(a));const u=+L[L.length-1][0].slice(5);return u===12?`em ${a}`:`de janeiro a ${MESX[u-1]} de ${a}`};
  $('pf-anos').innerHTML=anos.map(a=>`<li><button class="chip" type="button" data-a="${a}">${a}</button></li>`).join('');
  $('pf-anos').addEventListener('click',e=>{const b=e.target.closest('[data-a]');if(b){ano=b.dataset.a;draw()}});
  const draw=()=>{
    const Y=F.anos[ano], per=ate(ano);
    $('pf-anos').querySelectorAll('.chip').forEach(c=>c.classList.toggle('on',c.dataset.a===ano));
    $('pf-kpis').innerHTML=`
      <div class="kpi"><span class="eyebrow">Entrou</span><b class="num" style="color:var(--l)">${R(Y.rec)}</b><span>impostos, taxas e repasses, ${per}</span></div>
      <div class="kpi"><span class="eyebrow">Pago pela Prefeitura</span><b class="num" style="color:var(--b)">${R(Y.pago)}</b><span>dinheiro que saiu do caixa, ${per}</span></div>
      <div class="kpi"><span class="eyebrow">Empresas que receberam</span><b class="num">${nf(Y.nforn)}</b><span>as 10 maiores ficaram com ${Math.round(Y.top10/Y.forn_tot*100)}% do que foi pago a empresas</span></div>
      <div class="kpi"><span class="eyebrow">Custo da Câmara</span><b class="num" style="color:var(--c)">${R(Y.cam)}</b><span>pago pela Câmara, ${per}</span></div>`;
    // mês a mês
    const L=F.meses.filter(m=>m[0].startsWith(ano)), mx=Math.max(...L.map(m=>Math.max(m[1],m[2])),1);
    $('pf-mes-sub').textContent=`Em milhões de reais, ${per}. Os meses seguintes aparecem quando a Prefeitura enviar os dados ao TCE.`;
    $('pf-meses').innerHTML=Array.from({length:12},(_,i)=>{const m=L.find(x=>+x[0].slice(5)===i+1);
      return `<div class="pm${m?'':' vz'}" title="${m?`${MESX[i]}: entrou ${R(m[1])}, pago ${R(m[2])}`:'sem dados ainda'}"><div class="pm-b">${m?`<i class="e" style="height:${m[1]/mx*100}%"><span>${Math.round(m[1]/1e6)}</span></i><i class="s" style="height:${m[2]/mx*100}%"><span>${Math.round(m[2]/1e6)}</span></i>`:''}</div><small>${MES[i]}</small></div>`}).join('');
    // receitas
    const tg=Y.grp.reduce((s,g)=>s+g[1],0)||1;
    $('pf-grp').innerHTML=Y.grp.slice(0,10).map((g,i)=>`<li><span class="num mute">${i+1}</span><span class="nm">${esc(g[0])}</span><b class="num">${R(g[1])}</b><span class="br"><i style="width:${g[1]/Y.grp[0][1]*100}%;background:var(--l)"></i></span></li>`).join('')
      +(Y.grp.length>10?`<li><span></span><span class="nm mute">Outras ${Y.grp.length-10} fontes</span><b class="num mute">${R(Y.grp.slice(10).reduce((s,g)=>s+g[1],0))}</b></li>`:'');
    // câmara
    $('pf-cam').innerHTML=`<p class="pf-big num">${R(Y.cam)}</p><p style="margin:0 0 10px">foi o que a Câmara pagou ${per}: cerca de <b>${R(Y.cam/Y.n)}</b> por mês.</p>
      <p class="mute" style="margin:0;font-size:14px">É o equivalente a ${(Y.cam/Y.pago*100).toLocaleString('pt-BR',{maximumFractionDigits:1})}% do que a Prefeitura pagou no mesmo período. Inclui salários dos vereadores e funcionários, contas e serviços. <a href="/vereadores/">Veja o que cada vereador fez</a>.</p>`;
    // fornecedores
    $('pf-forn-sub').textContent=`As empresas que mais receberam ${per}. Ao todo, ${nf(Y.nforn)} empresas receberam pagamentos.`;
    let n=10; const mxf=Y.top[0]?Y.top[0][2]:1;
    const lista=()=>{$('pf-forn').innerHTML=Y.top.slice(0,n).map((f,i)=>`<li><span class="num mute">${i+1}</span><div><b>${esc(f[1])}</b><small>CNPJ ${cnpj(f[0])} · ${nf(f[3])} ${f[3]===1?'pagamento':'pagamentos'}</small><span class="br"><i style="width:${f[2]/mxf*100}%"></i></span></div><b class="num">${R(f[2])}</b></li>`).join('');
      $('pf-mais').hidden=n>=Y.top.length};
    $('pf-mais').onclick=()=>{n=Y.top.length;lista()}; lista();
    $('pf-pf').innerHTML=`Fora desta lista: <b>${R(Y.prop)}</b> pagos em nome da própria Prefeitura, em geral salários e repasses internos, e <b>${R(Y.pf)}</b> em ${nf(Y.npf)} pagamentos a pessoas físicas. Os nomes das pessoas não são mostrados, para proteger a privacidade.`;
  };
  draw();
};

P.vereador=function(id){
  const v=V.find(x=>x.id===id); if(!v)return; const i=v.i;
  document.documentElement.style.setProperty('--tint',`hsl(${hue(i)} 85% 94%)`);
  document.documentElement.style.setProperty('--deep',`hsl(${hue(i)} 55% 26%)`);
  const t=v.P+v.A+v.F, cm=v.cm||{P:0,A:0,F:0}, tc=cm.P+cm.A+cm.F;
  $('kpis').innerHTML=`
    <div class="kpi kpi-pres"><span class="eyebrow">Presença nas reuniões</span><div class="pres">${ring(v,56)}<b class="num">${v.P} de ${t}</b></div><span>reuniões em que esteve presente e votou, desde ${mesAno(D.pri.replace(/-/g,''))} · <span class="${v.F?'bad':''}">${v.F} ${v.F===1?'falta':'faltas'}</span></span></div>
    <div class="kpi"><span class="eyebrow">Presença nas comissões</span><b class="num">${tc?Math.round(cm.P/tc*100)+'%':'–'}</b><span>${tc?`${cm.P} de ${tc} reuniões · ${cm.F} ${cm.F===1?'falta':'faltas'}`:'sem lista de presença registrada'}</span></div>
    <div class="kpi"><span class="eyebrow">Propostas desde a posse</span><b class="num" style="color:var(--b)">${nf(v.tot)}</b><span>${nf(v.cat.b)} pedidos de melhoria no bairro · ${nf(v.cat.c)} cobranças à Prefeitura · ${nf(v.cat.l)} projetos de lei</span></div>
    <div class="kpi"><span class="eyebrow">Viagens oficiais</span><b class="num" style="color:var(--c)">${nf((v.vg||[]).length)}</b><span>${(v.vg||[]).length?brl.format(v.vgt||0)+' em despesas':'nenhuma registrada'}</span></div>`;
  $('kpis').insertAdjacentHTML('afterend',`<div class="tipos"><p class="eyebrow">Na contagem oficial da Câmara, desde a posse</p>
    <ul>${TIPOS.map(([k,pl,sg])=>`<li><b class="num">${nf(v.tp[k])}</b><span>${v.tp[k]===1?sg:pl.toLowerCase()}</span></li>`).join('')}</ul>
    <small>Os mesmos números que aparecem na busca da Câmara por autor, contando também as propostas feitas junto com outros vereadores.${v.url?` <a href="${esc(v.url)}" target="_blank" rel="noopener">Ficha oficial ↗</a>`:''}</small></div>`);
  // o que propôs
  $('picks').innerHTML=bar5(v)+ORDER.map(c=>`<button class="pick k-${c} num" type="button" data-c="${c}" ${v.cat[c]?'':'disabled'}><i></i><span>${CAT[c][0]}</span><b>${nf(v.cat[c])}</b><span class="ar" aria-hidden="true">›</span></button>`).join('');
  $('picks').addEventListener('click',e=>{const p=e.target.closest('.pick');if(p&&!p.disabled)openCat(p.dataset.c,i)});
  // lista com abas
  const minhas=IT.filter(it=>it[6].includes(i)); let cat='';
  $('tabs').innerHTML=`<li><button class="chip${cat?'':' on'}" type="button" data-k="">Todas<small>${nf(minhas.length)}</small></button></li>`+ORDER.filter(c=>v.cat[c]).map(c=>`<li><button class="chip${cat===c?' on':''}" type="button" data-k="${c}">${CAT[c][3]}s<small>${nf(v.cat[c])}</small></button></li>`).join('').replace('Proposta de leis','Propostas de lei');
  const draw=()=>pager($('lista'),cat?minhas.filter(it=>it[4]===cat):minhas,false,CEL?5:10);
  $('tabs').addEventListener('click',e=>{const b=e.target.closest('[data-k]');if(!b)return;cat=b.dataset.k;$('tabs').querySelectorAll('.chip').forEach(x=>x.classList.toggle('on',x===b));draw()}); draw();
  // onde pediu
  const b=minhas.filter(it=>it[4]==='b');
  const bai=[...b.reduce((m,it)=>it[10]?m.set(it[10],(m.get(it[10])||0)+1):m,new Map())].sort((a,b)=>b[1]-a[1]).filter(x=>x[1]>=2).slice(0,6);
  const th=themeCount(b).slice(0,6), mx=bai.length?bai[0][1]:1;
  $('onde').innerHTML=(bai.length?`<p class="h3" style="margin-top:0">Bairros com mais pedidos</p><ol class="rank">${bai.map(([n,c])=>`<li><span class="ti">${svg(ICON.pin,16)}</span><span class="nm"><a href="/bairros/?q=${encodeURIComponent(n)}">${esc(n)}</a></span><b class="num">${nf(c)}</b><span class="br"><i style="width:${c/mx*100}%"></i></span></li>`).join('')}</ol>`:`<p class="mute">${b.length?'Poucos pedidos com bairro identificado no texto.':'Nenhum pedido de melhoria em bairro desde a posse.'}</p>`)
    +(th.length?`<p class="h3">Assuntos mais pedidos</p><ul class="themes">${th.map(([k,n])=>`<li><span class="ti">${svg(ICON[TH[k][1]],18)}</span><span>${esc(TH[k][0])}</span><b class="num">${nf(n)}</b></li>`).join('')}</ul>`:'');
  const meusReps=D.rep.filter(g=>g.items.some(it=>it[6].includes(i)));
  $('reps-v').innerHTML=''; listaReps($('reps-v'),meusReps,3);
  $('reps-n').textContent=meusReps.length?`${nf(meusReps.length)} ruas com pedidos repetidos têm pelo menos um pedido de ${v.ap}.`:'';
  // votos
  if($('loc')){
    const L=v.loc;
    if(!L||!L.length){$('s-voto24').hidden=true}else{
      const lc=v.lc, m=D.locm, tipo=m==null?'':lc>=m+5?'concentrado em poucos bairros':lc<=m-5?'espalhado pela cidade':'nem concentrado nem espalhado';
      $('locc').innerHTML=`${v.vot?`${esc(v.ap)} teve <b class="num">${nf(v.vot)}</b> votos. `:''}<b class="num">${lc}%</b> deles vieram destes 5 locais de votação: um voto ${tipo}${m!=null?` (a média da Câmara é <span class="num">${m}%</span>)`:''}. Abaixo, se ele faz pedidos para esses bairros.`;
      $('loc').innerHTML=L.map((r,n)=>{const p=r[4]==null?`<p class="lpd mute">Sem pedidos com esse nome de bairro</p>`:r[4]?`<p class="lpd ok"><b class="num">${nf(r[4])}</b> ${r[4]===1?'pedido dele':'pedidos dele'} aqui</p>`:`<p class="lpd no"><b class="num">0</b> pedidos dele aqui</p>`;
        return `<article class="lcard"><span class="lnum">${n+1}º</span><b class="lpc num">${String(r[3]).replace('.',',')}%</b><span class="lvt num">${nf(r[2])} votos</span><h3>${esc(r[1]||'—')}</h3><p class="lsc">${esc(r[0])}</p>${p}</article>`}).join('');
    }
  }
  if($('jt')){
    const lin=x=>{const w=V.find(y=>y.id===x[0]);return w?`<li><a href="${urlV(w)}">${esc(w.ap)}</a><span class="pill">${esc(w.part)}</span><b class="num">${x[1]}%</b><i style="--p:${x[1]}%"></i></li>`:''};
    const jt=v.jt||[];
    $('jt').innerHTML=jt.length<2?'<p class="mute">Ainda há poucas votações divididas para comparar.</p>':
      `<p class="h3" style="margin-top:0">Vota mais junto com</p><ul class="jt">${jt.slice(0,3).map(lin).join('')}</ul>
       <p class="h3">Vota mais diferente de</p><ul class="jt jt-n">${jt.slice(-3).reverse().map(lin).join('')}</ul>
       <p class="mute small">Porcentagem de vezes em que os dois votaram igual nas ${nf(D.ndiv||0)} votações em que a Câmara se dividiu.</p>`;
    const g=v.gov||[0,0], pc=g[1]?Math.round(g[0]/g[1]*100):null;
    const todos=V.filter(w=>w.gov&&w.gov[1]).map(w=>w.gov[0]/w.gov[1]*100), med=todos.length?Math.round(todos.reduce((s,x)=>s+x,0)/todos.length):null;
    const lo=Math.max(0,Math.floor((Math.min(...todos)-4)/10)*10), esc_=x=>((x-lo)/(100-lo)*100).toFixed(1);
    const pos=pc==null?null:todos.filter(x=>x>g[0]/g[1]*100).length+1;
    $('gov').innerHTML=pc==null?'<p class="mute">Não votou em projetos da Prefeitura registrados no sistema.</p>':
      `<div class="gov num"><b>${pc}%</b><span>a favor dos projetos enviados pela Prefeitura<br>${nf(g[0])} de ${nf(g[1])} votos</span></div>
       <div class="gbar" aria-hidden="true">${todos.map(x=>`<i style="left:${esc_(x)}%"></i>`).join('')}<i class="me" style="left:${esc_(g[0]/g[1]*100)}%"></i></div>
       <div class="gleg num"><span>${lo}%</span><span>100%</span></div>
       <p class="small">Média da Câmara: <b class="num">${med}%</b>. ${pos===1?'É o índice mais alto':pos===todos.length?'É o índice mais baixo':'É o '+pos+'º índice mais alto'} de apoio aos projetos da Prefeitura, entre ${todos.length} vereadores.</p>
       <p class="mute small">Cada ponto é um vereador; o vermelho é ${esc(v.ap)}. Apoiar ou não a Prefeitura não é bom nem ruim por si só: mostra de que lado cada um costuma ficar.</p>`;
  }
  $('votos').innerHTML=`<div class="vote num"><div><b>${nf(v.vs)}</b><span>vezes sim</span></div><div class="n"><b>${nf(v.vn+v.va)}</b><span>${v.va?'não ou abstenção':'vezes não'}</span></div></div>
    ${v.naos.length?`<p class="h3">Quando não votou “sim”</p>${naosHTML(v)}`:`<p class="mute" style="margin:12px 0 0">Votou “sim” em todas as votações com voto registrado.</p>`}`;
  $('com').innerHTML=comHTML(v);
  $('ant').innerHTML=antHTML(v);
  $('vgs').innerHTML=(v.vg&&v.vg.length)?AVISO_VG+vgHTML(v):`<p class="mute">${v.vg?'Nenhuma viagem oficial registrada no Portal da Transparência.':'Dado ainda não coletado.'}</p>`;
  // compartilhar
  const link=SITE+urlV(v).slice(1), txt=`${v.ap} desde a posse: ${pctPres(v)??'–'}% de presença, ${nf(v.tot)} propostas. Veja tudo no Radar Bragança: ${link}`;
  $('wa').href='https://wa.me/?text='+encodeURIComponent(txt);
  $('cp').onclick=async e=>{try{await navigator.clipboard.writeText(link);e.target.textContent='Link copiado'}catch(_){e.target.textContent=link}};
  // anterior / próximo
  const S=V.slice().sort(ORD.nome), k=S.indexOf(v), ant=S[(k+S.length-1)%S.length], prox=S[(k+1)%S.length];
  $('pn').innerHTML=`<a href="${urlV(ant)}">← ${esc(ant.ap)}</a><a href="/vereadores/">Todos os vereadores</a><a href="${urlV(prox)}">${esc(prox.ap)} →</a>`;
};

P.bairros=function(){
  $('bl').innerHTML=D.bairros.slice(0,300).map(b=>`<option value="${esc(b)}"></option>`).join('');
  $('chips').innerHTML=D.bairros.slice(0,14).map(b=>`<li><button class="chip" type="button" data-b="${esc(b)}">${esc(b)}</button></li>`).join('');
  let tm;
  function bairro(q){
    document.dispatchEvent(new CustomEvent('radar:bairro',{detail:q}));
    const host=$('bres'), k=norm(q.trim()), city=k.length===0;
    $('chips').querySelectorAll('.chip').forEach(x=>x.classList.toggle('on',norm(x.dataset.b)===k));
    try{history.replaceState(null,'',location.pathname+(city?'':'?q='+encodeURIComponent(q.trim()))+location.hash)}catch(_){}
    if(!city&&k.length<3){host.innerHTML='<div class="panel"><p class="mute" style="margin:0">Continue digitando: preciso de pelo menos 3 letras.</p></div>';return}
    const items=city?IT:IT.filter(it=>it.n.includes(k));
    const official=D.bairros.find(name=>norm(name)===k);
    const report=city?'':'<p><a class="btn gh" href="/demandas/?bairro='+encodeURIComponent(official||q.trim())+'">Relatar um problema neste bairro</a></p>';
    if(!items.length){host.innerHTML=`<div class="panel"><p class="mute" style="margin:0">Nada encontrado para “${esc(q)}”. Confira a grafia ou tente só uma parte do nome.</p>${official?report:''}</div>`;return}
    const cnt=new Map(); items.forEach(it=>it[6].forEach(a=>cnt.set(a,(cnt.get(a)||0)+1)));
    const top=[...cnt.entries()].sort((a,b)=>b[1]-a[1]), mx=top[0][1];
    const th=themeCount(items.filter(it=>it[4]==='b'||it[4]==='c')).slice(0,city&&CEL?3:5);
    const reps=city?[]:D.rep.filter(g=>g.items.some(it=>it.n.includes(k))).slice(0,3);
    host.innerHTML=`<div class="panel">
     <div class="ph"><span class="big num">${nf(items.length)}</span><p>${city?'propostas para <b>a cidade inteira</b> até agora':`${items.length===1?'proposta cita':'propostas citam'} <b>${esc(q.trim())}</b> até agora`}</p></div>
     ${report}
     <div class="two">
       ${city?'':`<div><h3>Quem mais pediu</h3><ol class="rank">${top.slice(0,5).map(([a,n])=>`<li>${av(a)}<span class="nm"><a href="${urlV(V[a])}">${esc(V[a].ap)}</a> <span class="mute" style="font-weight:400">· ${esc(V[a].part)}</span></span><b class="num">${nf(n)}</b><span class="br"><i style="width:${n/mx*100}%"></i></span></li>`).join('')}</ol>
         ${top.length>5?`<p class="mute" style="font-size:13.5px;margin:10px 0 0">Mais ${top.length-5} vereadores também citaram.</p>`:''}</div>`}
       ${th.length?`<div><h3>O que mais pedem</h3><ul class="themes">${th.map(([t,n])=>`<li><span class="ti">${svg(ICON[TH[t][1]],18)}</span><span>${esc(TH[t][0])}</span><b class="num">${nf(n)}</b></li>`).join('')}</ul></div>`:''}
       ${city&&!CEL?`<div><h3>Bairros mais citados</h3><ul class="themes">${D.bairros.slice(0,5).map((b,i)=>`<li><span class="ti">${svg(ICON.pin,18)}</span><button class="lnk" type="button" data-b="${esc(b)}">${esc(b)}</button><b class="num">${nf(D.bairrosn[i])}</b></li>`).join('')}</ul></div>`:''}
     </div>
     ${reps.length?`<p class="h3" style="margin-top:24px">Problemas que voltam aqui</p><div class="reps">${reps.map(repHTML).join('')}</div>`:''}
     <p class="h3" style="margin-top:24px">${city?'As propostas mais recentes da cidade':'Os pedidos mais recentes'}</p><div id="blist"></div></div>`;
    const list=$('blist');
    const topics=themeCount(items).filter(([key])=>Object.hasOwn(TH,key));
    const resultCount=document.createElement('span');
    resultCount.className='bairro-topic-count';
    resultCount.setAttribute('role','status');

    const renderList=(key='')=>{
      const matches=key?items.filter(it=>it[8]===key):items;
      resultCount.textContent=nf(matches.length)+(matches.length===1?' proposta':' propostas');
      pager(list,matches,true,city&&CEL?2:4);
    };
    if(topics.length>1){
      const bar=document.createElement('div');
      bar.className='bairro-topic-bar';
      const field=document.createElement('div');
      field.className='bairro-topic-field';
      const label=document.createElement('label');
      label.htmlFor='bairro-topic';
      label.textContent='Filtrar por assunto';
      const select=document.createElement('select');
      select.id='bairro-topic';
      select.className='bairro-topic-select';
      select.append(new Option('Todos os assuntos',''));
      topics.forEach(([key])=>select.append(new Option(TH[key][0],key)));
      select.addEventListener('change',()=>renderList(select.value));
      field.append(label,select);
      bar.append(field,resultCount);
      list.before(bar);
    }
    renderList();
  }
  $('bq').addEventListener('input',e=>{clearTimeout(tm);tm=setTimeout(()=>bairro(e.target.value),150)});
  document.addEventListener('click',e=>{const b=e.target.closest('[data-b]');if(b){$('bq').value=b.dataset.b;bairro(b.dataset.b);$('busca').scrollIntoView({block:'start',behavior:reduce?'auto':'smooth'})}});
  const q0=new URLSearchParams(location.search).get('q')||''; $('bq').value=q0; bairro(q0);
  listaReps($('reps'),D.rep,CEL?4:9);
};

P.propostas=function(){
  const tot=ORDER.reduce((s,c)=>s+(D.catot[c]||0),0), lei=D.catot.l||0, hom=D.catot.h||0;
  $('hsub').textContent=`São ${nf(tot)} propostas desde a posse. `+(lei?`Para cada proposta de lei, ${(hom/lei).toLocaleString('pt-BR',{maximumFractionDigits:1})} homenagens. `:'')+'Toque em um grupo para ler cada uma.';
  $('split').innerHTML=ORDER.map(c=>`<i class="k-${c}" style="flex:${D.catot[c]||0} 1 0"></i>`).join('');
  $('cats').innerHTML=ORDER.map(c=>`<button class="cat k-${c}" type="button" data-c="${c}"><span class="ci">${svg(ICON[CAT[c][2]],26)}</span><span class="cv num">${nf(D.catot[c]||0)}</span><span class="cn">${CAT[c][0]} <span class="now">até agora</span></span><span class="cd">${CAT[c][1]}</span><span class="go">Ver todas →</span></button>`).join('');
  $('cats').addEventListener('click',e=>{const b=e.target.closest('[data-c]');if(b)openCat(b.dataset.c,null)});
  // busca livre em todas as propostas
  const category=new URLSearchParams(location.search).get('categoria');
  let tm, cat=ORDER.includes(category)?category:'';
  $('ptabs').innerHTML=`<li><button class="chip on" type="button" data-k="">Todas</button></li>`+ORDER.map(c=>`<li><button class="chip" type="button" data-k="${c}">${CAT[c][0]}</button></li>`).join('');
  const draw=()=>{const k=norm($('pq').value.trim());const L=IT.filter(it=>(!cat||it[4]===cat)&&(!k||it.n.includes(k)));
    $('pcount').textContent=`${nf(L.length)} ${L.length===1?'proposta':'propostas'}`;pager($('plista'),L,true,CEL?6:12)};
  $('ptabs').addEventListener('click',e=>{const b=e.target.closest('[data-k]');if(!b)return;cat=b.dataset.k;$('ptabs').querySelectorAll('.chip').forEach(x=>x.classList.toggle('on',x===b));draw()});
  $('pq').addEventListener('input',()=>{clearTimeout(tm);tm=setTimeout(draw,180)}); draw();
};

P.sobre=function(){
  $('m-pres').innerHTML=`<b>Contamos como presente quem votou.</b> Em cada reunião da Câmara, quem votou (sim, não, abstenção, ou o presidente, que não vota) estava lá. Quem aparece como “ausente” em todas as votações da reunião teve falta.<br><br>Foram ${D.sess} reuniões${D.pri?' de '+dt(D.pri):''} até ${D.ult?dt(D.ult):'agora'}. <b>A Câmara só começou a registrar o voto de cada vereador em ${D.pri?mesAno(D.pri.replace(/-/g,'')):'2026'}.</b> Antes disso não há registro, e o site não acusa ninguém por esse período.<br><br>Reuniões com votação só “de braço levantado”, sem lista de nomes, não entram. A lista oficial de frequência da Câmara é feita em outros momentos da reunião e pode dar números um pouco diferentes.`;
  $('m-sal').innerHTML=`O valor é o mesmo para os ${V.length} e foi fixado pela <a href="${esc(D.sal.u)}" target="_blank" rel="noopener">${esc(D.sal.lei)}</a>. É o valor bruto. O contador da página inicial é uma estimativa: ${V.length} salários por mês, proporcional ao tempo desde a posse, sem 13º nem outros pagamentos.`+(D.sal.confirmado?'':' <b>O valor de R$ '+nf(D.sal.v)+' foi publicado pela imprensa local e ainda precisa ser conferido no texto oficial.</b>');
  $('m-com').textContent=`Comissões são grupos de vereadores que estudam os projetos antes da votação: Finanças e Orçamento, Justiça e Redação, Educação e Cultura, e Assuntos Socioeconômicos. Contamos as ${nf(D.ncom||0)} reuniões de comissão${D.pricom?' desde '+dt(D.pricom):''} que têm lista de presença no sistema. Cada vereador só é contado nas comissões de que faz parte. Reunião sem lista não entra: falta de registro não é falta do vereador.`;
  if($('m-loc'))$('m-loc').textContent=`Os votos de 2024 são os dados oficiais do TSE, somados por escola onde se vota. O bairro de cada escola é o que a Justiça Eleitoral informa. Mostramos as 5 escolas onde cada vereador teve mais votos e quantos pedidos de melhoria ele fez para aquele bairro. “Voto concentrado” quer dizer que boa parte dos votos veio dessas 5 escolas; na média da Câmara, ${D.locm??'–'}%. Atenção: o eleitor vota perto de onde morava quando tirou o título, que nem sempre é onde mora hoje. Por isso o cruzamento mostra uma tendência, não uma regra.`;
  if($('m-blo'))$('m-blo').textContent=`“Com quem vota” olha só as ${nf(D.ndiv||0)} votações em que a Câmara se dividiu, ou seja, em que pelo menos um vereador votou diferente. Quando todos votam igual, não dá para comparar ninguém. Para cada dupla de vereadores, contamos quantas vezes os dois votaram igual. Só comparamos duplas que votaram juntas pelo menos 8 vezes. “Projetos da Prefeitura” são as ${nf(D.nexe||0)} votações de projetos enviados pelo prefeito. A porcentagem é de votos “sim”. Ausências não contam.`;
  $('m-vot').textContent=`Só entram as votações em que o sistema da Câmara registra o voto de cada vereador: ${nf(D.nvot)}${D.pri?' desde '+dt(D.pri):''}. Em ${nf(D.unan)} delas, todos votaram igual.`;
  $('m-erro').innerHTML=`Escreva para <b>${esc(CONFIG.contato)}</b> com o link da proposta ou da página. A correção é feita rápido.`;
};

window.Radar=P;
})();
