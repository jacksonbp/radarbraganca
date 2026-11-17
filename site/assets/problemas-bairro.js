(() => {
  const panel = document.getElementById('problemas-bairro');
  if (!panel) return;
  const title = document.getElementById('problemas-titulo');
  const note = document.getElementById('problemas-nota');
  const list = document.getElementById('problemas-lista');
  const isPreview = ['localhost', '127.0.0.1'].includes(location.hostname);
  const normalize = value => value.normalize('NFD').replace(/[\u0300-\u036f]/g, '').toLowerCase().trim().replace(/^bairro (?:do |da |de )?/, '');
  const example = [
    {bairro: 'Bairro do Cruzeiro', titulo: 'Poste apagado', local: 'Via pública', situacao: 'Encaminhado'},
    {bairro: 'Bairro do Cruzeiro', titulo: 'Limpeza de área pública', situacao: 'Resolvido'}
  ];
  const element = (tag, text, className) => {
    const el = document.createElement(tag);
    if (text) el.textContent = text;
    if (className) el.className = className;
    return el;
  };
  let request;
  function records() {
    if (isPreview) return Promise.resolve(example);
    if (!request) {
      request = (async () => {
        const url = new URL(panel.dataset.receptor);
        url.searchParams.set('painel', 'bairros');
        const response = await fetch(url, {cache: 'no-store'});
        if (!response.ok) throw new Error('Painel indisponível');
        const data = await response.json();
        if (!data.ok || !Array.isArray(data.problemas)) throw new Error('Painel indisponível');
        return data.problemas;
      })().catch(error => { request = null; throw error; });
    }
    return request;
  }
  function card(item, showBairro) {
    const card = element('li', '', 'problema-card');
    const info = element('div', '', 'problema-info');
    info.append(element('h4', item.titulo));
    const location = [showBairro ? item.bairro : '', item.local].filter(Boolean).join(' · ');
    if (location) info.append(element('p', location));
    const done = item.situacao === 'Resolvido';
    card.append(info, element('span', item.situacao, done ? 'problema-status resolvido' : 'problema-status'));
    if (/^\d{4}-\d{2}-\d{2}$/.test(item.atualizado || '')) {
      info.append(element('small', 'Atualizado em ' + item.atualizado.split('-').reverse().join('/')));
    }
    return card;
  }
  let renderId = 0;
  async function render(search) {
    const id = ++renderId;
    const key = normalize(search);
    title.textContent = key ? 'Problemas relatados · ' + search.trim() : 'Problemas dos bairros';
    list.replaceChildren();
    note.textContent = 'Carregando o acompanhamento…';
    try {
      const all = await records();
      if (id !== renderId) return;
      const items = all.filter(item => !key || normalize(item.bairro).includes(key))
        .sort((a, b) => (b.atualizado || '').localeCompare(a.atualizado || ''));
      note.textContent = isPreview ? 'Demonstração com dados fictícios.' : 'Relatos públicos revisados pela equipe do Radar Bragança.';
      const resolved = items.filter(item => item.situacao === 'Resolvido').length;
      const counts = [items.length, items.length - resolved, resolved];
      const labels = ['Demandas publicadas', 'Em aberto', 'Resolvidas'];
      const overview = element('div', '', 'painel-contadores');
      counts.forEach((count, index) => {
        const metric = element('div', '', 'painel-metrica metrica-' + index);
        metric.append(element('span', labels[index]), element('strong', String(count)));
        overview.append(metric);
      });
      const progress = element('div', '', 'painel-progresso');
      const percent = items.length ? Math.round(resolved / items.length * 100) : 0;
      progress.append(element('span', 'Resolução das demandas'), element('b', items.length ? percent + '%' : 'Sem registros'));
      const track = element('div', '', 'painel-trilha');
      const fill = element('div', '', 'painel-preenchimento');
      fill.style.width = percent + '%';
      track.append(fill);
      progress.append(track);
      const workspace = element('div', '', 'painel-registros');
      const toolbar = element('div', '', 'painel-barra');
      const filters = element('div', '', 'painel-filtros');
      filters.setAttribute('role', 'group');
      filters.setAttribute('aria-label', 'Filtrar demandas por situação');
      const result = element('div');
      result.setAttribute('aria-live', 'polite');
      const buttons = [];
      function draw(index) {
        const matching = items.filter(item => index === 0 || (item.situacao === 'Resolvido') === (index === 2));
        buttons.forEach((button, i) => button.setAttribute('aria-pressed', String(index === i)));
        result.replaceChildren();
        if (matching.length) {
          const cards = element('ul', '', 'problema-cards');
          matching.forEach(item => cards.append(card(item, !key || normalize(item.bairro) !== key)));
          result.append(cards);
        } else {
          const empty = element('div', '', 'painel-vazio');
          empty.append(element('h3', items.length ? 'Nenhuma demanda nesta situação' : 'O acompanhamento começa com o seu relato'));
          empty.append(element('p', items.length ? 'Selecione outro filtro para consultar os registros.' : 'Envie um problema pelo Voz do Bairro. Após revisão e publicação pela equipe, ele aparecerá neste painel.'));
          result.append(empty);
        }
      }
      ['Todas', 'Em aberto', 'Resolvidas'].forEach((label, index) => {
        const button = element('button', label + ' (' + counts[index] + ')');
        button.type = 'button';
        button.addEventListener('click', () => draw(index));
        buttons.push(button);
        filters.append(button);
      });
      const report = element('a', 'Relatar um problema', 'painel-relatar');
      report.href = '/demandas/' + (search.trim() ? '?bairro=' + encodeURIComponent(search.trim()) : '');
      toolbar.append(filters, report);
      workspace.append(toolbar, result);
      list.append(overview, progress, workspace);
      draw(0);

    } catch (_) {
      if (id === renderId) note.textContent = 'O acompanhamento está indisponível no momento.';
    }
  }
  document.addEventListener('radar:bairro', event => render(event.detail));
  render(document.getElementById('bq').value).then(() => {
    if (location.hash === '#problemas-bairro') panel.scrollIntoView();
  });
})();

