# Radar Bragança

Site que mostra o que cada vereador de Bragança Paulista-SP faz desde a posse (01/01/2025):
presença, propostas e votos. Só dados oficiais da Câmara, atualizados todo dia por um robô.

## O que tem aqui

| Pasta / arquivo | O que é |
|---|---|
| `site/index.html` | A página do site. |
| `site/dados.js` | Os dados que o robô baixou da Câmara. |
| `site/fotos/` | Fotos oficiais dos vereadores (do site camarabp.sp.gov.br). |
| `coletor/coletar.py` | O robô que vai à Câmara e baixa tudo. |
| `.github/workflows/atualizar.yml` | Faz o GitHub rodar o robô todo dia às 4h e republicar o site. |

## De onde vêm os dados

A Câmara de Bragança **não usa o SAPL** (o sistema de Hortolândia). Ela usa o **SISCAM**
(braganca.siscam.com.br). O robô usa:

- **Autores → Vereadores**: nome, apelido, partido, cargo.
- **Proposituras** (indicações, requerimentos, moções, pedidos de informação) e **Projetos**
  (de lei, lei complementar, resolução, decreto legislativo, emenda à Lei Orgânica), filtrados por
  vereador, exportados em CSV.
- **Votações** nominais do plenário: quem votou a favor, contra, absteve-se, estava ausente.
- **Frequências**: ausências justificadas e licenças médicas.
- **camarabp.sp.gov.br/vereadores**: foto e e-mail oficial do gabinete.

## Antes de divulgar (importante)

1. **Salário**: o valor de R$ 15.147,29 veio da imprensa local, sobre a Resolução nº 2/2024.
   Confira no texto oficial (Imprensa Oficial de 25/04/2024, pág. 10). Se estiver certo, abra
   `coletor/coletar.py`, troque `"confirmado": False` por `"confirmado": True` e rode o robô de novo.
2. **Contato para correções**: abra `site/index.html`, procure `CONFIG` no começo do código e
   preencha `contato:` com um e-mail ou Instagram do projeto (não use número pessoal).
3. **Confira 2 ou 3 vereadores na mão**: abra a ficha oficial e compare com o crachá do site.

## Como colocar no ar (GitHub, de graça)

1. Crie uma conta em github.com e um repositório **público** (ex.: `radarbraganca`).
2. Envie todos estes arquivos para o repositório (botão "Add file → Upload files", arrastando as pastas).
3. No repositório: **Settings → Pages → Source: GitHub Actions**.
4. Vá em **Actions → Atualizar dados e publicar → Run workflow** para rodar a primeira vez.
5. O site fica em `https://www.bragancaterraquerida.com.br/` (também abre por `https://jacksonbp.github.io/radarbraganca/`).

## Rodar o robô no seu computador

```bash
python coletor/coletar.py
```

Leva uns 5 a 10 minutos: ele espera 1,5 segundo entre cada pedido para não pesar no servidor da Câmara.
Se a coleta vier estranha (poucos vereadores, poucas propostas, queda grande em relação à última),
ele para e não troca os dados antigos.
