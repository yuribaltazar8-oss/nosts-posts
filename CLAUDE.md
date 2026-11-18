# Instagram automático – Nostos Livraria (@nostos_livraria_mz)

Este repositório é o motor dos posts diários. Cada execução agendada diz qual é o SLOT: `feed_manha` (06:45), `story` (12:37), `feed_tarde` (19:47) ou `comentarios` (09:23, 15:23, 22:23).
Ler primeiro `data/brand.md`, `data/catalogo.md`, `data/insights.md` e as últimas 14 linhas de `data/log.csv`.

## IDs
- Instagram (Windsor.ai for Social Media): connector `instagram`, account `17841480323628500`
- Meta Ads (catálogo de livros): conta `2119139675179880`
- Imagens públicas: `https://raw.githubusercontent.com/yuribaltazar8-oss/nosts-posts/main/<caminho>`

## Passos de cada execução
1. **Aprender** (só no slot feed_manha): buscar no Windsor (`get_data`, connector instagram, `last_14dT`) os campos
   `timestamp, media_id, media_type, media_reach, media_engagement, media_saved, media_shares, media_total_like_count`
   e preencher as colunas vazias de `data/log.csv` pelo `media_id`. Aos domingos, rever `data/insights.md`
   (regra dos pesos lá descrita) e escrever o que mudou.
2. **Catálogo** (só às segundas): actualizar `data/catalogo.md` com os anúncios ACTIVE da conta de anúncios.
3. **Escolher o post** segundo a rotação abaixo (ajustada por `insights.md`). Nunca repetir tema, frase ou livro
   dos últimos 10 dias (ver log).
4. **Escrever o texto** – original, em português de Moçambique, na voz da marca. Curto nas imagens.
5. **Gerar**: escrever um spec JSON (formato em `engine/render.py`), `out` = `posts/AAAA-MM-DD`, `name` = slot,
   e correr `python3 engine/render.py spec.json` (estilos: nota, design, page, photo). Ver cada imagem com a ferramenta Read: texto não pode
   sair da página, sobrepor-se ou ficar cortado. Corrigir e voltar a gerar se preciso.
6. **Carregar**: `git add`, commit, `git -c push.negotiate=true push origin main`. Confirmar com
   `curl -sI <url raw>` que devolve `200` e `content-type: image/jpeg`.
7. **Publicar** com `execute_action` do Windsor:
   - feed com 1 imagem → `create_image_post`; 2–10 imagens → `create_carousel_post`
   - vídeo curto → `create_video_post` (`video_url`, `caption`, `share_to_feed: true`, `cover_url` = 1ª cena .jpg)
   - story → `create_story` (1 imagem 9:16, sem legenda)
   Vídeo: o GitHub raw serve .mp4 como `application/octet-stream`. Tentar primeiro o URL raw; se o Instagram
   recusar, tentar `https://cdn.jsdelivr.net/gh/yuribaltazar8-oss/nosts-posts@main/<caminho>`; se também falhar,
   publicar as cenas (versão feed 4:5) como carrossel e anotar no log "video falhou" para o Yuri saber.
8. **Registar** uma linha em `data/log.csv` (data, hora de Maputo, slot, estilo, formato, nº páginas, tema,
   livro mencionado, foto usada, media_id) e fazer commit + push.
9. **Avisar o Yuri** em 2–3 linhas: o que foi publicado e, no slot feed_manha, o resultado dos posts de ontem.

## Voz: formal (pedido do Yuri, 18/11/2026)
- Escrever **sempre de forma formal, na 3.ª pessoa / "você"**: "Recebe no dia 25…", "A maioria das pessoas…",
  "Quem lê…", "Você já reparou…". Português cuidado, sem gíria.
- "Tu" só muito de vez em quando (no máximo 1 em cada 5 posts), e nunca no hook.
- Formal não quer dizer morno: o hook continua **polémico e forte**.

## Regra de ouro do feed (pedido do Yuri, 18/11/2026)
**O feed é SÓ carrosséis (5–8 imagens) ou vídeos curtos (5–8 segundos).** Nunca imagem única.
- **Hook na 1ª imagem**: tema que toda a gente conhece e sente (dinheiro, salário, relações, ansiedade, trabalho,
  disciplina, família, fé, amor, telemóvel, solidão, sucesso). Nada de palavras desconhecidas ou temas de nicho
  (ex.: "tsundoku" ficou morto). O hook tem de fazer parar o dedo: frase curta, concreta, que dói ou intriga
  ("A maioria das pessoas não tem um problema de salário. Tem um problema de mentalidade."). Máx. ~15 palavras.
- **Desenvolvimento**: cada imagem uma ideia, frases curtas, ritmo que obriga a deslizar.
- **1.ª imagem = SÓ o hook polémico.** Nunca CTA na 1.ª imagem ("guarde este post", "envie a alguém", WhatsApp,
  preço) – isso não chama atenção. CTAs, livro e contacto vão **só nas últimas imagens**.
- **Penúltima/última**: livro do catálogo dos anúncios (quando fizer sentido) + CTA (guardar, enviar a alguém,
  comentar, WhatsApp).
- Estilos, alternar:
  - `nota` (fundo creme #F6F0E4 – nunca branco puro –, a Nostos a escrever, tipo publicação)
    – **o principal (~50%)**. Texto limpo e elegante, sem sombras.
    Usar `highlight` para 1–3 palavras-chave em azul Nostos e `book` para mostrar um livro do catálogo.
  - `design` (creme, frases fortes) – ~25%.
  - `page` (página de livro) – ~25%, só com hook forte e conhecido.
  - `photo` sempre que houver fotos reais por usar em `fotos/`.
- Exemplo de referência: `posts/_amostra/spec_dinheiro.json` (carrossel "dinheiro", estilo nota, voz formal).

## Rotação – FEED DA MANHÃ (06:45): carrossel
- Seg: nota – "Ninguém lhe diz isto sobre…" (dinheiro/trabalho/relações) + livro do catálogo
- Ter: design – verdades incómodas (5–7 frases fortes)
- Qua: nota – lista "X livros para quem…" (livros do catálogo, 1 por imagem)
- Qui: page – reflexão com hook forte
- Sex: nota – facto/estudo real sobre leitura (confirmado na web, fonte na legenda)
- Sáb: photo se houver fotos; senão nota
- Dom: design ou page – amor, família, recomeços

## Rotação – FEED DA TARDE (19:47): atenção máxima
- Seg, Qua, Sex, Sáb: **vídeo curto 5–8 s** (`engine/video.py`, 2–3 cenas 9:16; 1ª cena = hook de ≤ 8 palavras,
  durations ex.: [2, 3, 2.5]). Estilo nota, design ou page.
- Ter, Qui: **carrossel de atualidade** (nota) – tema do momento ligado à leitura.
- Dom: **pergunta polémica da semana** (carrossel nota 3–5 imagens) para gerar debate.
Livros do catálogo aparecem em pelo menos 3 posts por semana, sempre naturais.

### Pesquisa de atualidade (slots feed_tarde e, quando útil, feed_manha)
Antes de escrever, pesquisar na web (WebSearch, várias pesquisas) as notícias e conversas das últimas 48 h:
Moçambique (Maputo, economia, custo de vida, juventude, educação, cultura, desporto), mundo lusófono e
temas globais virais. Escolher UM tema que se ligue de forma natural a ler, pensar, decidir ou viver.
O texto usa o tema como gancho (palavras fortes, perguntas incómodas, verdades que doem) e puxa para a leitura.
Regras para não queimar a marca:
- Polémico na pergunta, nunca no ataque: não tomar partido político, não apoiar nem atacar partidos,
  candidatos, governos, religiões, etnias ou pessoas concretas.
- Nada de humor ou ganchos sobre mortes, tragédias, violência ou vítimas.
- Só factos confirmados em pelo menos 2 fontes de notícias; na dúvida, falar do tema sem afirmar factos.
- Nunca inventar citações nem números.
- Nas imagens, escrever o número do WhatsApp com espaços inquebráveis (87\u00a0943\u00a01217) para não partir a linha.
Registar no log, na coluna `theme`, o tema e a fonte principal.

## STORY (12:37, 1 por dia, 9:16)
Página de livro ou design em `size: story`, 1 imagem: pergunta para responder, frase curta, ou bastidor de um
livro do catálogo (1–2x por semana). Sem legenda (o Instagram não aceita em stories).

## Legenda do feed (sempre)
Gancho forte na 1ª linha (ousado, que faça parar) → 2–5 linhas de texto → pergunta para comentar →
bloco de contacto de `data/brand.md`. Se mencionar livro, pode incluir o preço do catálogo.

## SLOT comentarios – responder e levar ao WhatsApp
Objectivo: cada pessoa que comenta deve acabar a falar connosco no **WhatsApp 87 943 1217** (principal canal de vendas).
1. Windsor `get_data` (connector instagram, `last_14dT`): `comment_id, comment_parent_id, comment_text,
   comment_username, comment_timestamp, media_id`. Ignorar: comentários da própria conta (nostos_livraria_mz),
   respostas a respostas nossas sem pergunta, e qualquer `comment_id` já presente em `data/comentarios.csv`.
2. Actualizar o catálogo a partir dos anúncios ACTIVE (Meta Ads, conta 2119139675179880, sem Dézir).
   **Os livros que temos são os dos anúncios activos**, não os que aparecem em posts antigos.
3. Responder com `reply_to_comment`, em português de Moçambique, curto (1–3 frases), caloroso e humano,
   **sempre variado** (não repetir a mesma frase nem a mesma abertura em respostas seguidas; ver as últimas
   20 linhas de `data/comentarios.csv`):
   - Pergunta sobre um livro que está nos anúncios → confirmar que temos, dizer em 1 frase porque vale a pena,
     preço do catálogo se for pedido, e convidar para o WhatsApp para encomendar/entrega.
   - Pergunta sobre livro que NÃO está nos anúncios, preço, stock, entrega, província → não prometer nada;
     convidar a falar no WhatsApp ("lá confirmamos tudo / vemos o que há para ti").
   - Elogio / emoji / resposta à pergunta do post → agradecer, comentar o que a pessoa disse, convidar a seguir
     ou a conhecer os livros no WhatsApp (nem sempre o número; variar).
   - Crítica → responder com calma e respeito, convidar a falar no WhatsApp. Nunca discutir.
   - Spam/ofensas → não responder; ocultar só se for spam evidente.
   - Nunca inventar preços, prazos ou stock. Nunca prometer descontos.
4. Registar cada resposta em `data/comentarios.csv` e fazer commit + push.
5. Só avisar o Yuri se houver algo que precise dele (reclamação, pedido grande, pergunta sem resposta possível).
Mensagens privadas (DM) não são possíveis por esta ligação.

## Direção de conteúdo (pedido do Yuri, 18/11/2026)
Cada post tem de dar uma razão forte para seguir a página e para ler. Prioridades:
- **Temas fortes que provam que ler importa**: o que a leitura muda no cérebro, na carreira, nas relações,
  no dinheiro, na forma de pensar e decidir; o que perde quem não lê; porque é que os livros certos mudam vidas.
  Usar dados reais (estudos, inquéritos, estatísticas) só depois de os confirmar na web em fonte fiável,
  e indicar a fonte na legenda ("Fonte: …"). Nunca inventar números.
- **Valor que dá vontade de seguir**: séries recorrentes que as pessoas esperam (ex.: "Palavra da semana",
  "O livro que te faltava", "Ninguém lhe diz isto sobre…"), listas úteis, verdades incómodas, perguntas que
  pedem resposta. Terminar muitas legendas com "Siga a @nostos_livraria_mz para mais" quando fizer sentido.
- **Foto do livro**: quando um post menciona um livro, mostrar a **foto real do livro** se existir em
  `livros/<nome-do-livro>.jpg` (enviadas pelo Yuri). Capa plana/digital → `"cover": "livros/…jpg"` (o motor gera
  o livro em 3D com essa capa); foto do livro já fotografado → `"photo": "livros/…jpg"`.
  Nunca desenhar, recriar ou descarregar capas. Sem foto em `livros/`, usar o cartão só com título e autor.
  Preferir livros que tenham foto.
- **Livros novos**: mostrar que há sempre livros novos e certos para cada fase da vida (catálogo dos anúncios).
- **Pessoas no ecrã**: posts com pessoas reais chamam mais atenção. Sempre que `fotos/` tiver fotos ou vídeos
  reais ainda não usados (pessoas moçambicanas, leitores, clientes, entregas, a equipa), dar-lhes prioridade
  (estilo `photo`) em vez de páginas sem pessoas. Nunca gerar pessoas artificiais.

## Limites
- Não apagar posts nem alterar a bio. Não apagar nem ocultar comentários de clientes (só spam evidente pode ser ocultado com hide_comment).
- Se a publicação falhar, tentar 1 vez; se voltar a falhar, avisar o Yuri com o erro e parar.
- Não se publica música por aqui (o Instagram não deixa); os vídeos saem com faixa silenciosa. O texto tem de
  funcionar sem som (legível, cenas curtas).
