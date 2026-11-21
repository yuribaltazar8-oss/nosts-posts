# Instagram automático – Nostos Livraria (@nostos_livraria_mz)

Este repositório é o motor dos posts diários. Cada execução agendada diz qual é o SLOT: `feed_manha` (06:45), `story` (12:37), `reel_meio` (13:13), `feed_tarde` (19:47) ou `comentarios` (09:23, 15:23, 22:23).
Ler primeiro `data/brand.md`, `data/catalogo.md`, `data/insights.md` e as últimas 14 linhas de `data/log.csv`.

## IDs
- Instagram (Windsor.ai for Social Media): connector `instagram`, account `17841480323628500`
- Meta Ads (catálogo de livros): conta `2119139675179880`
- Imagens públicas: `https://raw.githubusercontent.com/yuribaltazar8-oss/nosts-posts/main/<caminho>`

## Passos de cada execução
1. **Aprender – TODOS OS DIAS** (no slot feed_manha; nos slots feed_tarde e story ler só `insights.md`): buscar no Windsor
   (`get_data`, connector instagram, `last_14dT`) os campos `timestamp, media_id, media_type, media_reach, media_views,
   media_engagement, media_saved, media_shares, media_total_like_count, media_total_comments_count, media_follows,
   media_profile_visits, media_reel_avg_watch_time, media_reel_skip_rate` e preencher `data/log.csv` pelo `media_id`.
   Depois calcular o **Score viral** de cada post (fórmula em `data/insights.md`), actualizar o ranking e as
   "Fórmulas vencedoras / a evitar" em `insights.md` e escrever no aviso ao Yuri o melhor e o pior post de ontem
   e o que se vai copiar ou mudar hoje. Aos domingos, revisão maior dos pesos (regra em `insights.md`).
1b. **Datas comemorativas** (todos os dias, slots feed_manha e story): ver `data/datas.md`. Se hoje for uma data,
   o post do dia é sobre ela (imagens próprias da data no estilo da marca: creme/azul Nostos, Garamond, livro em 3D
   quando fizer sentido, assinatura "Leia. Regresse a si."; nada de clip-art, ícones genéricos, imagens da
   internet ou imagens geradas por IA). Se for amanhã, o story de hoje anuncia-a. Datas maiores (23 Abr, 25 Jun,
   25 Dez) podem ter carrossel + vídeo + story. No aviso ao Yuri, lembrar as datas dos próximos 7 dias
   (para ele preparar fotos ou promoções, se quiser).
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

## Objectivo: retenção máxima e viralização (pedido do Yuri, 18/11/2026)
Cada post tem de fazer as pessoas pararem, irem até ao fim, comentarem e enviarem a alguém. A Nostos deve ser
vista em todo o país como **a referência**: o conteúdo que as pessoas dizem "isto é o melhor que já vi".
Antes de publicar, o post tem de passar este teste (se falhar um ponto, reescrever):
1. **Pára o dedo em 1 segundo?** Hook curto, concreto e com tensão (contradição, verdade que dói, promessa clara,
   pergunta que incomoda). Sem introduções, sem "Olá", sem contexto antes do impacto.
2. **Abre um ciclo que só fecha no fim?** A 1.ª imagem cria uma pergunta na cabeça da pessoa; a resposta
   completa só chega na penúltima. Numerar quando ajudar ("3 sinais…", "1/6").
3. **Cada imagem puxa a seguinte?** Terminar imagens com gancho ("Mas o pior não é isso.", "O 3.º é o que
   ninguém admite.", "E é aqui que tudo muda."). Uma ideia por imagem, poucas palavras, letra grande.
4. **Há uma recompensa real?** Uma ideia nova, útil ou que muda a forma de ver – algo que a pessoa queira guardar.
5. **Dá vontade de comentar?** Terminar com pergunta de lado (A ou B?, "Concorda ou discorda?",
   "Qual destes é você?", "Complete a frase: …"). Perguntas fáceis de responder numa palavra geram mais comentários.
6. **Dá vontade de enviar a alguém?** Ideias que as pessoas usam para falar com outra pessoa
   ("Envie a quem precisa de ler isto hoje"), identificação forte ("Isto é para quem…").
7. **Vídeo: a 1.ª cena entende-se sem som em < 1 s**, movimento ou texto logo no 1.º frame, nada de ecrã parado
   no início; terminar de forma que dê vontade de ver outra vez (loop).
8. **Qualidade de referência**: zero erros de português, design limpo e consistente, nada genérico ou
   "copiado da internet". Melhor publicar menos texto e mais forte.
9. **Tem os códigos da Nostos?** Assinatura "Leia. Regresse a si." no fim, série com nome fixo, azul Nostos,
   #regresseasi – ver "Códigos da Nostos" em `data/brand.md`. Sem isto, o post não sai.
Os dados mandam: se `insights.md` mostrar que um tipo de hook, tema, formato, estilo ou hora rende mais,
**usar mais esse** e deixar cair o que rende menos (mantendo ~20% de testes novos para descobrir o próximo vencedor).

## Conteúdo de peso: clássicos e grandes autores (pedido do Yuri, 18/11/2026)
Quem vê a página tem de sentir que **está a perder muito se não seguir**. Para isso, pelo menos 3 posts por
semana trazem conhecimento sólido de grandes pensadores e livros de referência:
- Filosofia e vida: Aristóteles, Séneca, Marco Aurélio, Epicteto, Maquiavel, Nietzsche, Dostoiévski, Tolstói…
- Negócios, dinheiro e carreira: Philip Kotler (marketing), Peter Drucker, Napoleon Hill, Dale Carnegie,
  T. Harv Eker, Morgan Housel…
- Psicologia e relações: Viktor Frankl, Daniel Kahneman, Robert Greene…
Formatos que funcionam: "O que Aristóteles diria sobre o seu salário", "5 ideias de Kotler que qualquer pessoa
que vende precisa de saber", "O que Séneca escreveu há 2 000 anos sobre ansiedade", "1 livro, 5 lições".
Regras de rigor (a página tem de ser **referência de confiança**):
- Cada ideia, data ou citação é confirmada na web em ≥ 2 fontes fiáveis antes de publicar; fonte na legenda
  ("Fonte: Aristóteles, Ética a Nicómaco, Livro II"). Na dúvida, não publicar essa ideia.
- Citações literais: só de autores clássicos em domínio público (ex.: Aristóteles, Séneca, Marco Aurélio,
  Maquiavel, Dostoiévski), curtas e com obra indicada. Autores modernos (Kotler, Drucker, Kahneman…):
  explicar as ideias com palavras nossas e indicar o autor e a obra, sem copiar frases.
- Nunca atribuir a um autor uma frase que ele não escreveu (muitas "citações" da internet são falsas – confirmar).
- Ligar sempre a ideia à vida real em Moçambique (salário, negócio, família, trabalho) – é isso que a torna viral.
- Preferir autores/livros que estão no catálogo dos anúncios (clássicos e filosofia é o anúncio com
  melhores resultados) e, no fim, mostrar o livro.

## Identidade moçambicana (pedido do Yuri, 18/11/2026)
A Nostos valoriza a cultura de Moçambique e as pessoas têm de o sentir. **Pelo menos 1–2 posts por semana**
(feed ou story) com voz moçambicana, e um post dedicado nas datas nacionais.
- **Autores moçambicanos**: Paulina Chiziane, Mia Couto, José Craveirinha, Noémia de Sousa,
  Ungulani Ba Ka Khosa, Lília Momplé, Luís Bernardo Honwana, Rui Knopfli e outros reconhecidos.
  Formatos: "Uma frase moçambicana que devia estar em todas as casas", "O que Paulina Chiziane nos ensina sobre…",
  "Escritores moçambicanos que todo o país devia ler", perfil do autor (quem é, porque importa, 1 ideia forte).
- **Figuras históricas já falecidas** (ex.: Eduardo Mondlane, Samora Machel, Josina Machel): só citações sobre
  temas que unem – educação, trabalho, unidade, cultura, dignidade, juventude. **Nunca** ligar a partidos,
  eleições, governos actuais ou polémicas políticas; nunca usar para criticar ou elogiar quem está no poder.
  Pessoas vivas da política: nunca.
- **Provérbios e sabedoria popular** (changana, ronga, macua, sena, ndau…): só com a versão original e a
  tradução confirmadas em fonte fiável; indicar a língua.
- **Datas nacionais** (post temático, sem política): 3 de Fevereiro (Dia dos Heróis Moçambicanos),
  7 de Abril (Dia da Mulher Moçambicana), 25 de Junho (Independência), 4 de Outubro (Dia da Paz e Reconciliação),
  Dia da Cidade de Maputo (10 de Novembro). Confirmar a data na web antes de publicar.
- **Vida real moçambicana** nos exemplos: o salário que acaba antes do mês, o chapa, a família alargada,
  o negócio de bairro, a xima de domingo, Maputo, Matola, Beira, Nampula… sempre com respeito.
Regras de rigor e direitos:
- Toda a citação é confirmada em ≥ 2 fontes fiáveis (de preferência a obra ou o discurso original) e leva
  autor + obra/discurso + ano na legenda. Muitas frases que circulam atribuídas a moçambicanos famosos são falsas:
  se não houver confirmação, não usar.
- Autores com obra protegida (todos os acima): citação **curta** (1–2 frases), entre aspas, com autor e obra,
  para comentar ou homenagear. Nunca poemas inteiros, estrofes longas ou páginas copiadas.
- Livros de autores moçambicanos que não estão nos anúncios: não prometer stock; convidar a perguntar no
  WhatsApp ("pergunte-nos no WhatsApp").
- Nunca usar fotos de pessoas reais tiradas da internet (só fotos em `fotos/`). Retrato do autor = cartão
  tipográfico com o nome.

## Carrosséis-anúncio com fotos reais dos livros (pedido do Yuri, 21/11/2026)
Fotos em `fotos/livros/*_anuncio.jpg` (lista e preços em `data/catalogo.md`). Usar estes dois formatos com frequência
(pelo menos 3x por semana no feed, alternando com os outros):
1. **"3 livros para aprender…"** (ex.: "…a dizer não", "…a lidar com dinheiro", "…a decidir melhor"):
   imagem 1 = hook forte; imagens 2–4 = um livro por imagem (foto real grande + 1 frase do que ensina);
   última = CTA (WhatsApp 87 943 1217, "Leia. Regresse a si.", logo).
2. **"O livro primeiro"**: imagem 1 = a foto do livro em destaque (bonita, com um hook curto por cima);
   imagens seguintes = o que o livro ensina (3–5 ideias, uma por imagem, confirmadas); última = CTA.
Qualidade: as imagens têm de parecer **caras, profissionais e chamativas** – foto do livro grande e nítida
(melhorar nitidez/contraste/cor da foto real se preciso), composição limpa, azul Nostos + creme fortes.
As fotos são anúncios já feitos no branding da Nostos (preço + WhatsApp): **usar tal como estão, sem tapar
o preço nem o texto** (Yuri, 21/11). Usar a versão `*_4x5.jpg` (1080×1350, proporção certa do carrossel, fundo
desfocado da própria foto nas margens) e não pôr texto novo por cima. O texto/hook vai nas imagens próprias
(hook, ideias, CTA) entre as fotos. Nunca alterar a capa nem inventar livros.

## Perfil do livro e imagens bonitas de livros (pedido do Yuri, 18/11/2026)
- **"Perfil do livro"** (série, 1–2x por semana, carrossel 5–7 imagens): 1) hook sobre o problema que o livro
  resolve; 2) o livro em destaque (3D a partir da capa real, grande e bonito); 3) quem é o autor (1 frase,
  confirmada); 4–5) as 3 ideias mais fortes; 6) "Livro-casa para quem…"; 7) assinatura + WhatsApp.
  Também em story 1x por semana (1 imagem: livro em 3D + 1 frase + "Peça no WhatsApp").
- **Imagens de livros**: usar as capas reais em `livros/` para o motor gerar o livro em 3D em composições
  cuidadas (livro grande ao centro, fundo creme ou azul Nostos, uma frase curta). Fotos reais de livros abertos,
  estantes e entregas em `fotos/` têm prioridade sempre que existirem.
- Nunca desenhar, inventar ou descarregar capas, e nunca gerar imagens com IA (pessoas ou cenas falsas).
  Se faltar a capa de um livro que se quer mostrar, usar o cartão tipográfico (título + autor) e, no aviso da
  manhã, pedir ao Yuri a foto desse livro para `livros/`.

## Regra de ouro do feed (pedido do Yuri, 18/11/2026)
**O feed é SÓ carrosséis (5–8 imagens) ou reels de livros (8–14 segundos, com som).** Nunca imagem única.
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
  - `nota` (fundo creme #F6EFE0 (creme claro de papel de livro) – nunca branco puro –, a Nostos a escrever, tipo publicação)
    – **o principal (~50%)**. Letra de livro (Garamond) sobre papel de livro claro, igual às páginas mas mais
    claro. Texto limpo e elegante, sem sombras.
    Usar `highlight` para 1–3 palavras-chave em azul Nostos e `book` para mostrar um livro do catálogo.
  - `design` (creme, frases fortes) – ~25%.
  - `page` (página de livro) – ~25%, só com hook forte e conhecido.
  - `photo` sempre que houver fotos reais por usar em `fotos/`.
- Exemplo de referência: `posts/_amostra/spec_dinheiro.json` (carrossel "dinheiro", estilo nota, voz formal).

## Rotação – FEED DA MANHÃ (06:45): carrossel
- Seg: nota – "Ninguém lhe diz isto sobre…" (dinheiro/trabalho/relações) + livro do catálogo
- Ter: design – verdades incómodas (5–7 frases fortes)
- Qua: nota – lista "X livros para quem…" (livros do catálogo, 1 por imagem)
- Qui: page – "Página que fica": ideia de um clássico/grande autor ligada à vida de hoje (confirmada, fonte na legenda)
- Sex: nota – facto/estudo real sobre leitura (confirmado na web, fonte na legenda)
- Sáb: photo se houver fotos; senão "Perfil do livro" (nota, livro em 3D)
- Dom: design ou page – amor, família, recomeços

## REELS = LIVROS + SOM (pedido do Yuri, 18/11/2026 – manda sobre as regras de vídeo abaixo)
- **NÃO usar `livros/dinheiro-e-emocional_foto.jpg` nem `livros/dinheiro-e-emocional.jpg` em vídeos** (o Yuri pediu,
  18/11: qualidade insuficiente). Usar só material novo de alta qualidade.
- **"As pessoas compram vendo os livros, não os textos."** Os carrosséis são de texto; os **vídeos são dos livros**:
  o livro aparece em TODAS as cenas (foto/vídeo real na mão, aberto, na estante, capa 3D real). Nada de cenas só de texto.
- Motor: **`engine/livros.py`** (exemplo: `posts/2026-11-18/livros_reel_teste1.json`). Cenas `intro` (hook a escrever-se
  num cartão creme Nostos), `book` (1 frase curta por corte: o que o livro resolve), `outro` (azul Nostos, logo,
  "Leia. Regresse a si.", WhatsApp). Usar `photo`/`clip` de `fotos/` e `livros/` (reais), `focus`/`zoom` para variar
  o enquadramento; `cover` (capa real → 3D) quando não houver foto.
- Formatos que vendem: "O livro para quem…", "3 livros para quem…" (1 livro por corte), "1 livro, 3 lições",
  página aberta com a frase do livro (como a referência do Yuri: mão a segurar o livro aberto em frente à estante).
- **Som obrigatório**: o Yuri escolheu música livre de direitos. `engine/livros.py` junta sempre a batida original Nostos
  (`engine/musica.py`, `"music": "afro"` ou `"lofi"`, `"seed"` diferente em cada vídeo, mesmo `bpm` dos cortes).
  Nunca usar músicas de terceiros (o Instagram corta o som ou bloqueia).
- Pessoas: só fotos/vídeos reais (de `fotos/`, `livros/` ou enviados pelo Yuri). Não há gerador de imagens aqui e não se
  inventam pessoas. Pedir ao Yuri, no aviso, vídeos curtos (5–10 s) de mãos a segurar cada livro do catálogo.
- **Vídeo só de texto = proibido** (Yuri, 18/11, sobre a amostra `posts/_amostra/reel_homem.mp4`: "o conteúdo é bom,
  mas para carrossel, não para vídeo" e "está rápido"). Ideias fortes só de texto vão para carrossel.
  O vídeo segue a referência do Yuri: imagens reais de livros (mão a segurar/abrir o livro, estante, páginas),
  pouco texto por cena e tempo para ler: ≥ 3 s por frase curta (≤ 10 palavras), no máximo 1 frase por cena.
  Sem filmagens reais em `fotos/videos/` ou capas em `livros/`, não se faz vídeo: carrossel + pedido ao Yuri.
- Hook (cena 1) = problema que a pessoa sente + o livro já visível. Pergunta → resposta só no fim (ciclo aberto).
- Verificar 8–10 frames (ffmpeg) com Read antes de publicar.

## Cadência: 3 publicações por dia (pedido do Yuri, 18/11/2026)
- 06:45 `feed_manha` – carrossel. · 12:37 `story`. · **13:13 `reel_meio`** – reel de livro **em teste** (Trial Reel).
  · 19:47 `feed_tarde` – reel de livro para todos os seguidores.
- **Trial Reels** (`create_video_post` com `trial_params: {"graduation_strategy": "SS_PERFORMANCE"}`): só aparece a
  quem não segue e o Instagram passa-o para o feed sozinho se render. Máximo **3 reels em teste ao mesmo tempo**
  (os `trial` dos últimos 3 dias no log); se já houver 3, o `reel_meio` sai normal. Registar `trial` na coluna `format`.
- O `feed_tarde` repete o formato/livro/hook do trial com melhor Score (ver `insights.md`) com outra ideia.

## Vídeos: feedback do Yuri (18/11/2026) – "mortos, sem sentido, não chamam atenção"
O vídeo de 18/11 ("Dizem que ler é luxo…", 3 cartões de texto com zoom lento) é o exemplo do que **não** fazer.
- **Usar `engine/reel.py`** (não `video.py`): texto a entrar parágrafo a parágrafo, cortes secos com punch-in,
  livro 3D a subir e a flutuar, cenas `photo` com fotos reais. Exemplo: `posts/_amostra/reel_dinheiro.json`.
- **Todo o vídeo gira à volta de um LIVRO REAL**, com imagem real: cena `book` com a capa de `livros/` (livro 3D
  grande) ou cena `photo` com fotos/vídeos reais de `fotos/`. Sem imagem real do livro → não fazer vídeo;
  fazer carrossel e, no aviso, pedir a foto ao Yuri.
- **Tem de ter sentido**: uma história simples – problema que a pessoa sente (cena 1, hook) → o que está por trás
  (cena 2) → o livro que resolve, em grande (cena 3) com "Leia. Regresse a si.". Nada de frases soltas/abstractas,
  nada de notícia colada à força. A atualidade só entra se ligar de forma óbvia ao livro mostrado.
- **Livros mais elaborados** (também nos carrosséis): mostrar o livro grande e bonito, dizer em concreto o que
  ensina (2–3 ideias), para quem é, e porque agora. Preferir sempre fotos reais de livros (abertos, na mão,
  estantes, entregas) quando existirem em `fotos/`.
- Antes de publicar, extrair 6–8 frames do vídeo (ffmpeg) e ver com Read: o 1.º frame já tem texto e o livro
  aparece grande e nítido.
- Enquanto `fotos/` estiver vazia e `livros/` só tiver 1 capa, pedir ao Yuri no aviso: fotos dos livros mais
  vendidos (capa de frente, livro aberto, na mão) e pequenos vídeos reais de livros/entregas.

## Rotação – FEED DA TARDE (19:47) e REEL_MEIO (13:13): reels de livros, todos os dias
- Ambos são **reels de livros** (`engine/livros.py`, com som). Variar: "O livro para quem…", "3 livros para quem…",
  "1 livro, 3 lições", página aberta com frase. Tema da atualidade só se ligar de forma óbvia ao livro.
- A pergunta polémica de domingo e o carrossel de atualidade passam para a legenda / carrossel da manhã.
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
"Leia. Regresse a si." → bloco de contacto de `data/brand.md` (com #regresseasi). Se mencionar livro, pode incluir o preço do catálogo.

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
   - Comentário "CASA" (ritual da marca) → resposta curta e calorosa, variação de "Bem-vindo(a) a casa.";
     às vezes sugerir um livro-casa no WhatsApp.
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
  Preferir livros que tenham foto. Para cortar a capa de uma foto tirada à mão, usar transformação de
  perspectiva (ver como foi feita `livros/dinheiro-e-emocional.jpg` a partir de `livros/dinheiro-e-emocional_foto.jpg`).
- **Variar sempre o formato**: carrossel de texto com o livro em 3D pequeno por baixo; páginas de livro;
  fotos do livro aberto ou de páginas reais (quando o Yuri as enviar para `fotos/`); listas; vídeos curtos.
  Nunca dois posts seguidos com o mesmo formato.
- **Livros novos**: mostrar que há sempre livros novos e certos para cada fase da vida (catálogo dos anúncios).
- **Pessoas no ecrã**: posts com pessoas reais chamam mais atenção. Sempre que `fotos/` tiver fotos ou vídeos
  reais ainda não usados (pessoas moçambicanas, leitores, clientes, entregas, a equipa), dar-lhes prioridade
  (estilo `photo`) em vez de páginas sem pessoas. Nunca gerar pessoas artificiais.

## Limites
- Não apagar posts nem alterar a bio. Não apagar nem ocultar comentários de clientes (só spam evidente pode ser ocultado com hide_comment).
- Se a publicação falhar, tentar 1 vez; se voltar a falhar, avisar o Yuri com o erro e parar.
- Não se publica música por aqui (o Instagram não deixa); os vídeos saem com faixa silenciosa. O texto tem de
  funcionar sem som (legível, cenas curtas).
