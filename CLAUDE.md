# Instagram automático – Nostos Livraria (@nostos_livraria_mz)

Este repositório é o motor dos posts diários. Cada execução agendada diz qual é o SLOT: `feed_manha` (06:45), `story` (12:37), `reel_meio` (13:13), `feed_tarde` (19:47) ou `comentarios` (09:23, 15:23, 22:23).
Ler primeiro `data/brand.md`, `data/catalogo.md`, `data/insights.md` e as últimas 14 linhas de `data/log.csv`.
**Fila primeiro:** em todos os slots de feed, ver `data/fila.md`. Se houver um post `pendente`
aprovado pelo Yuri, publicar esse (como está) em vez de criar um novo, e seguir as instruções da fila.

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
Fotos em `fotos/livros/*_anuncio.jpg` (lista e preços em `data/catalogo.md`). Usar estes dois formatos com moderação
(cerca de 1 em cada 3 posts – ver "Equilíbrio" abaixo), alternando com posts calmos:
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

## Todos os livros têm de sair (pedido do Yuri, 22/11/2026)
"Não use só romances. Quero que todos os livros saiam." Os posts rodam por **todo o catálogo** com foto
(`data/catalogo.md`: autoajuda, finanças, fé, clássicos, filosofia, romance, produtividade, poder…), não só
pelo género que rendeu mais.
- Antes de escolher o livro de um post, ver no log a última vez que cada livro do catálogo saiu e dar
  prioridade aos que **nunca saíram ou saíram há mais tempo**. Cada livro com foto deve aparecer pelo menos
  1 vez a cada 2 semanas.
- Nunca dois posts seguidos do mesmo género. Romance no máximo 1 post em cada 3.
- Listas "3/4 livros para quem…" ajudam a mostrar mais livros de uma vez – misturar géneros quando fizer sentido
  (ex.: ansiedade = Tolle + Carnegie + Robbins + Wilde).
- Os dados (insights) decidem o FORMATO e o tipo de gancho; o catálogo inteiro decide os LIVROS.
- Trial reels: no máximo 1 a cada 2 dias (rendem metade dos normais).

## Temas variados – NADA de "salário" a toda a hora (Yuri, 22/11/2026: "Você só fala de salário… não gostei dos posts")
- **Dinheiro/salário/custo de vida: no máximo 1 post por semana** (contar no log os últimos 7 dias antes de escolher).
  A palavra "salário" não aparece em mais nenhum gancho nessa semana.
- Rodar por esta roda de temas – nunca o mesmo tema 2 vezes no mesmo dia, nem em 2 dias seguidos no mesmo slot:
  amor e relações · amizade · família e filhos · fé e espiritualidade · ansiedade e paz interior · autoestima e
  coragem · solidão · perdão e recomeços · mistério e suspense · histórias que prendem (romance, thriller, clássicos) ·
  poder e pessoas difíceis · hábitos e disciplina · decisões e pensar melhor · propósito e sentido da vida ·
  Moçambique (autores, provérbios, datas) · curiosidades sobre livros e leitura · humor leve com livros e leitores.
- Os exemplos de gancho deste ficheiro que falam de salário são só exemplos de FORMA, não de tema.

## Tom misturado: nem tudo é sério – GENERALIZAR (Yuri, 22/11/2026: "Nós não vendemos só coisas sérias tipo coach";
"conversa no ChatGPT, por vezes um sorriso de meme etc! Generaliza")
Cerca de **1 em cada 3 posts (reels, carrosséis e stories) é leve/divertido**. Variar SEMPRE o formato – nunca o mesmo
formato divertido 2 vezes seguidas. Banco de formatos (inventar outros no mesmo espírito):
- **"Perguntei à IA…"** (`engine/chat.py` com `"style": "app"` – o preferido do Yuri: parecido com a app de IA do
  telemóvel, fundo preto, pergunta à direita em balão azul, resposta em texto corrido com ícones, barra de escrever
  em baixo; ou `"style": "ia"`): conversa curta e engraçada com uma IA genérica sobre
  livros ("Perguntei à IA que livro ler depois de um desgosto"). Aspecto genérico de app de IA, **sem logótipo,
  nome ou visual copiado do ChatGPT ou de outra marca**; os lados chamam-se "Eu" e "IA".
- **Conversa com a Nostos / com a estante / com o livro** (`engine/chat.py`, estilo creme/azul).
- **Reacções tipo meme com emoji grande** (`"react": "😭"`, "😂", "🙂", "😳", "🤡", "💀"…) no fim de uma conversa ou
  de um carrossel. Só emojis – **nunca fotos de memes com pessoas reais ou personagens com direitos**.
- **Humor de leitor**: "só vou ver livros", a pilha por ler a olhar para nós, ler no chapa, "já acabaste?",
  "o livro acabou e eu não estou bem", "livro emprestado que nunca voltou".
- **Trends/memes da semana** adaptados a livros: "POV:", "Ninguém: / Eu:", "Me at 2 AM", "Red flag ou green flag?",
  "Diga o seu signo e eu digo o livro", "Livros como pessoas que conhece", "Escolha um: A ou B", "Antes vs. depois
  de ler…". Pesquisar na web as trends da semana (Instagram/TikTok – Brasil, Portugal, Moçambique) e usar 1–2.
- **Nos reels**: o mesmo humor cabe no estilo aprovado (texto no topo, frases curtas, emoji de reacção no texto).
Regras: é encenação/piada da marca e tem de parecer piada – nunca apresentar como conversa real de um cliente,
nunca nomes/números reais, nunca inventar elogios ou testemunhos. O livro aparece sempre (foto real ou nome)
e a legenda tem a pergunta para comentar. Voz mais solta nestes posts, sem palavrões e sem gozar com ninguém.

## Equilíbrio: posts calmos sem preço (pedido do Yuri, 21/11/2026)
"A pessoa quer paz, ler, interessar-se e depois procurar saber mais." Não pôr banners de preço em todos os posts.
- **A maioria dos posts (~2 em cada 3) é natural e calma**: sem preço nem WhatsApp nas imagens; o livro aparece
  no seu contexto (página, ideia, foto limpa, vídeo real) e **o preço e o contacto ficam só na legenda**.
  Para estes, usar imagens sem preço: `fotos/videos/`, `*-capa` sem preço, capa em 3D, ou a foto `*_anuncio.jpg`
  recortada só ao livro e à mão (sem o preço/texto do anúncio).
- **Só ~1 em cada 3 posts** é carrossel-anúncio com as fotos `*_4x5.jpg` (preço + WhatsApp visíveis).
- Nunca dois posts seguidos com preço nas imagens. Registar no log, na coluna `style`, `anuncio` ou `calmo`.

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
**O feed é: 2 reels por dia (manhã e 13:13, estilo aprovado, som viral) + 1 carrossel à noite (5–8 imagens, letra grande e nítida).** Nunca imagem única.
- **Hook na 1ª imagem**: tema que toda a gente conhece e sente (dinheiro, salário, relações, ansiedade, trabalho,
  disciplina, família, fé, amor, telemóvel, solidão, sucesso). Nada de palavras desconhecidas ou temas de nicho
  (ex.: "tsundoku" ficou morto). O hook tem de fazer parar o dedo: frase curta, concreta, que dói ou intriga
  ("Há pessoas que nunca o abandonaram. Só deixaram de responder."). Máx. ~15 palavras.
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

## Rotação – FEED DA MANHÃ (06:45): tema do dia (agora em REEL, ver Cadência)
- Seg: nota – "Ninguém lhe diz isto sobre…" (dinheiro/trabalho/relações) + livro do catálogo
- Ter: design – verdades incómodas (5–7 frases fortes)
- Qua: nota – lista "X livros para quem…" (livros do catálogo, 1 por imagem)
- Qui: page – "Página que fica": ideia de um clássico/grande autor ligada à vida de hoje (confirmada, fonte na legenda)
- Sex: nota – facto/estudo real sobre leitura (confirmado na web, fonte na legenda)
- Sáb: photo se houver fotos; senão "Perfil do livro" (nota, livro em 3D)
- Dom: design ou page – amor, família, recomeços

## REELS – estilo e som APROVADOS pelo Yuri (22/11/2026) – manda sobre tudo o resto sobre vídeo
O Yuri viu os reels de teste com cartões creme e música Nostos e **não quer mais esse tipo de edição** ("eu pedi
para trocar"). TODOS os reels (reel_meio, feed_tarde, trial ou não) seguem agora isto:
- **Motor: `engine/sextante.py`** (ver o cabeçalho do ficheiro). `engine/livros.py`, `reel.py` e `video.py` com
  cartões creme **já não se usam** para reels. Exemplo aprovado: `posts/prontos/reel_desligar_a_cabeca.mp4`.
- **Estilo "Sextante" com cores Nostos**: texto curto no topo (2 linhas), creme com sombra, palavra-chave em creme
  sobre etiqueta azul; gancho a escrever-se; frases a entrar suaves; zoom lento; fecho azul com logo,
  "Leia. Regresse a si." e uma pergunta. Sem cartões/caixas creme, sem barras.
- **Imagens**: vídeos reais em `fotos/videos/` em ecrã inteiro; fotos de livros com `"kind": "photo"` + `"crop"`
  de `data/recortes.json` (livro + mão, sem preço). Livro novo sem recorte: medir com grelha (desenhar linhas de 100 px
  sobre `*_anuncio.jpg`, ver com Read) e acrescentar o recorte a `recortes.json`. Ver 6–8 frames antes de publicar.
- **Som = SONS VIRAIS escolhidos pelo Yuri** (`sons/`). "Quero sons virais e não mortos que ninguém conhece."
  - Usar só ficheiros de `sons/` (enviados pelo Yuri, a partir de reels em tendência ou dos reels da Sextante – Yuri, 23/11). Preferir os mais recentes;
    não repetir o mesmo som em 2 reels seguidos; registar no log (coluna `theme`) o som usado.
  - **Nunca** usar a batida gerada `engine/musica.py` nem música inventada.
  - Se `sons/` só tiver sons com mais de 7 dias ou já gastos (usados ≥ 3 vezes), continuar com o menos usado e,
    no aviso ao Yuri, pedir 2–3 sons novos em tendência (ele envia um reel com o som; extrair com
    `ffmpeg -i video.mp4 -vn -c:a aac sons/som_NN_<nome>.m4a`).
  - Uma vez por semana (domingo), pesquisar na web que sons/músicas estão em tendência nos Reels (Moçambique,
    Brasil, Portugal) e sugerir ao Yuri os nomes, para ele enviar os que quiser. Não descarregar música da internet.
  - Se o Instagram silenciar ou recusar um vídeo por causa do som, avisar o Yuri com o nome do som e não o usar mais.
- Fila primeiro: `data/fila.md`.

## Cadência: MAIS VÍDEOS – 3 reels por dia (pedido do Yuri, 22/11/2026: "Passe a postar mais vídeos! No período da manhã quero vídeos")
- **06:45 `feed_manha` – REEL** (já não é carrossel). Usa o tema do dia da "Rotação – FEED DA MANHÃ" abaixo,
  mas em vídeo (`engine/sextante.py`, som viral). · 12:37 `story`. · 13:13 `reel_meio` – reel.
  · **19:47 `feed_tarde` – CARROSSEL** (Yuri, 22/11: "de noite ou de tarde pode ser carrossel"), com o tema do dia.
- **Carrosséis com letra GRANDE e NÍTIDA** (Yuri, 22/11): corpo em Inter (sans) ≥ 72 px (padrão 80), títulos ≥ 90 px;
  Garamond só em títulos grandes ou assinatura, nunca em texto pequeno; no máximo ~25 palavras por imagem.
  `render.py` já usa por defeito `nota` em Inter 80 px (mínimo 72) – não baixar o tamanho.
- Fila primeiro (`data/fila.md`) em TODOS os slots (um item pendente sai no slot seguinte, seja qual for).
- **Trial Reels**: no máximo 1 a cada 2 dias, sempre no `reel_meio` (`trial_params: {"graduation_strategy":
  "SS_PERFORMANCE"}`); registar `trial` na coluna `format`. Os outros saem normais para todos os seguidores.
- Variar: 3 reels por dia com livros, géneros e ganchos diferentes (ver "Todos os livros têm de sair") e sons
  diferentes quando houver mais do que um em `sons/` (só música, nunca fala).
- O reel seguinte copia o formato/gancho do reel com melhor Score dos últimos 7 dias, com outra ideia e outros livros.

## Vídeos: feedback do Yuri (18/11/2026) – "mortos, sem sentido, não chamam atenção"
O vídeo de 18/11 ("Dizem que ler é luxo…", 3 cartões de texto com zoom lento) é o exemplo do que **não** fazer.
- Motor e estilo: ver "REELS – estilo e som APROVADOS" acima (`engine/sextante.py`).
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
- Ambos são **reels de livros** (`engine/sextante.py`, com som viral de `sons/`). Variar: "O livro para quem…", "3 livros para quem…",
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
- Os reels levam o som viral de `sons/` já dentro do vídeo; o texto tem de funcionar também sem som.
