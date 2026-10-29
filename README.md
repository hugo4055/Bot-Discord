# Bot-Discord (VoidBot)

Bot para Discord feito em Python com discord.py, preparado para deploy no Render.

## Comandos incluídos
- `/ajuda` — lista os comandos.
- `/ping` — latência do bot.
- `/userinfo` — informações de um membro.
- `/serverinfo` — informações do servidor.
- `/say` — envia uma mensagem, exigindo Gerenciar mensagens.
- `/limpar` — apaga de 1 a 100 mensagens, exigindo Gerenciar mensagens.
- Boas-vindas opcionais com `WELCOME_CHANNEL_ID`.
- Endpoint `/health` para monitoramento do Render.

## Configuração no Discord
1. Abra https://discord.com/developers/applications e crie uma aplicação.
2. Na aba **Bot**, crie/copiei o token e mantenha-o privado.
3. Em **Bot > Privileged Gateway Intents**, ative **Server Members Intent** para boas-vindas.
4. Em **OAuth2 > URL Generator**, marque `bot` e `applications.commands`.
5. Permissões recomendadas: View Channels, Send Messages, Embed Links, Read Message History e Manage Messages.
6. Abra a URL gerada e convide o bot para o servidor.
7. No Discord, ative Modo desenvolvedor em Configurações > Avançado para copiar IDs de servidor/canal.

## Deploy no Render
1. Entre em https://render.com e conecte o GitHub.
2. Selecione **New > Blueprint** e escolha este repositório. O Render lerá `render.yaml`.
3. Nas variáveis de ambiente, preencha `DISCORD_TOKEN` com o token real. Preencha `GUILD_ID` com o ID do servidor de teste e `WELCOME_CHANNEL_ID` com o ID do canal de boas-vindas, se desejar.
4. Veja os logs até aparecer `Logged in as ...`.
5. Teste `/ping` e `/ajuda`.

O serviço gratuito do Render pode suspender serviços web ociosos; confira os limites atuais se precisar de disponibilidade 24/7.

## Segurança
Nunca coloque o token em arquivos do GitHub, mensagens públicas ou capturas de tela. Se vazar, redefina-o no Developer Portal e atualize a variável no Render.

## Arquivos
- `bot.py`: código do bot.
- `requirements.txt`: dependências Python.
- `render.yaml`: configuração do Render Blueprint.
- `.env.example`: exemplo de variáveis (sem segredo real).
