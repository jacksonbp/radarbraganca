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
