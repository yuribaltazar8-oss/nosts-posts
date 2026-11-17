# Instagram automático – Nostos Livraria (@la_livraria_mz)

Este repositório é o motor dos posts diários. Cada execução agendada diz qual é o SLOT: `feed` ou `story`.
Ler primeiro `data/brand.md`, `data/catalogo.md`, `data/insights.md` e as últimas 14 linhas de `data/log.csv`.

## IDs
- Instagram (Windsor.ai for Social Media): connector `instagram`, account `17841480323628500`
- Meta Ads (catálogo de livros): conta `2119139675179880`
- Imagens públicas: `https://raw.githubusercontent.com/yuribaltazar8-oss/nosts-posts/main/<caminho>`

## Passos de cada execução
1. **Aprender** (só no slot feed): buscar no Windsor (`get_data`, connector instagram, `last_14dT`) os campos
   `timestamp, media_id, media_type, media_reach, media_engagement, media_saved, media_shares, media_total_like_count`
   e preencher as colunas vazias de `data/log.csv` pelo `media_id`. Aos domingos, rever `data/insights.md`
   (regra dos pesos lá descrita) e escrever o que mudou.
2. **Catálogo** (só às segundas): actualizar `data/catalogo.md` com os anúncios ACTIVE da conta de anúncios.
3. **Escolher o post** segundo a rotação abaixo (ajustada por `insights.md`). Nunca repetir tema, frase ou livro
   dos últimos 10 dias (ver log).
4. **Escrever o texto** – original, em português de Moçambique, na voz da marca. Curto nas imagens.
5. **Gerar**: escrever um spec JSON (formato em `engine/render.py`), `out` = `posts/AAAA-MM-DD`, `name` = slot,
   e correr `python3 engine/render.py spec.json`. Ver cada imagem com a ferramenta Read: texto não pode
   sair da página, sobrepor-se ou ficar cortado. Corrigir e voltar a gerar se preciso.
6. **Carregar**: `git add`, commit, `git -c push.negotiate=true push origin main`. Confirmar com
   `curl -sI <url raw>` que devolve `200` e `content-type: image/jpeg`.
7. **Publicar** com `execute_action` do Windsor:
   - feed com 1 imagem → `create_image_post`; 2–10 imagens → `create_carousel_post`
   - story → `create_story` (1 imagem 9:16, sem legenda)
8. **Registar** uma linha em `data/log.csv` (data, hora de Maputo, slot, estilo, formato, nº páginas, tema,
   livro mencionado, foto usada, media_id) e fazer commit + push.
9. **Avisar o Yuri** em 2–3 linhas: o que foi publicado e, no slot feed, o resultado do post de ontem.

## Rotação semanal do FEED (06:45)
- Seg: página de livro – carrossel de reflexão (4–6 páginas: title → sections → closing)
- Ter: design – frase forte (quote) + 1 página `book` com um livro do catálogo
- Qua: página de livro – uma palavra/conceito (`word`, 1 imagem). Só palavras com origem verdadeira e conhecida
  (ex.: metanoia, saudade, ubuntu, kintsugi, sonder…); nunca inventar etimologias.
- Qui: página de livro – livro em destaque (`book`) do catálogo, com texto que faz desejar ler
- Sex: design – carrossel "X livros para quem…" com livros do catálogo (3–6 páginas `book`)
- Sáb: foto real (estilo `photo`) se houver em `fotos/` uma foto ainda não usada; senão página de livro
- Dom: página de livro – carrossel leve e humano (amor, família, recomeços)
Mencionar livros em ~3 dos 7 dias, sempre de forma natural. Os outros dias são só sobre ler e viver.

## STORY (19:20, 1 por dia, 9:16)
Página de livro ou design em `size: story`, 1 imagem: pergunta para responder, frase curta, ou bastidor de um
livro do catálogo (1–2x por semana). Sem legenda (o Instagram não aceita em stories).

## Legenda do feed (sempre)
Gancho forte na 1ª linha (ousado, que faça parar) → 2–5 linhas de texto → pergunta para comentar →
bloco de contacto de `data/brand.md`. Se mencionar livro, pode incluir o preço do catálogo.

## Limites
- Não apagar posts, não alterar a bio, não responder a comentários sem o Yuri pedir.
- Se a publicação falhar, tentar 1 vez; se voltar a falhar, avisar o Yuri com o erro e parar.
- Não se publica música por aqui (o Instagram não deixa); não prometer som.
