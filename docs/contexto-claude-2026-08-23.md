# Contexto passado pelo Claude (sessão factory-cauteloso, 2026-08-23)

Thiago pediu explicitamente: "considere o Codex seu braço direito" -- e
pediu que eu te passasse contexto completo de como as coisas funcionam e
como estão agora, pra você absorver o máximo possível. Se restar dúvida
depois de ler isso e o que já está nos repos, a instrução dele é
perguntar direto pra ele, não adivinhar.

Não estou mexendo na sua sessão nem no seu git enquanto você trabalha --
isso aqui é só um arquivo novo, pra você ler quando parar.

## O ecossistema (visão geral)

Três categorias de repositório, todas do Thiago (`thiagopatzdorf`):

1. **`factory-cauteloso`** -- o orquestrador em si (onde eu, Claude, rodo
   principalmente). Lê Issues do GitHub com label `factory`, roteia por
   label `repo:*` pro repositório alvo, despacha pra um agente CLI,
   valida, mescla ou manda pra REWORK. `README.md` e `CLAUDE.md`/
   `FACTORY.md` nesse repo têm a arquitetura e a filosofia completas.
2. **`mybagcenter-site`** -- "o grande projeto", o produto real (loja
   e-commerce). Onde a maior parte do trabalho de negócio acontece.
3. **Repos de conhecimento compartilhado** -- criados 2026-08-22,
   clonados localmente em `~/repos/`:
   - `bug-learning-loop` -- bugs reais (qualquer projeto), causa raiz +
     fix + lição generalizável.
   - `compactacao` -- casos reais de desperdício de recurso (tokens,
     memória, processamento) identificado ou corrigido, mais um
     checklist de perguntas (`principios.md`).
   - Outros: `python` (ferramentas/benchmarks/training-data), `so`,
     `seguranca-e-infraestrutura`, `system-design`, `saas-free-tier-scout`,
     `linux`, `engenharia-de-controle-e-automacao`.

   **Regra que acabei de generalizar hoje**: antes de gastar tokens
   re-derivando uma investigação de causa-raiz ou de eficiência, qualquer
   agente permanente (você, eu, Gemini, Qwen, Grok, opencode, aider)
   deveria checar esses repos primeiro. Acabei de adicionar um
   `AGENTS.md` neste próprio repo (`poc-airflow/AGENTS.md`, ainda não
   commitado por você -- fica pra você decidir quando) apontando pra
   isso. O mesmo já está em `factory-cauteloso` (PR #56) e
   `mybagcenter-site` (PR #90).

## Como o roteamento/dispatch funciona (factory-cauteloso)

- `routing.resolve_model`: escolhe qual agente CLI despachar, consultando
  `~/.pomerode/agents.json` (o que o Pomerode -- projeto separado --
  reporta como `READY`, ou seja, instalado + autenticado). O pool padrão
  é `antigravity,grok,opencode,codex` -- você já é membro padrão.
- `config.MODEL_WORKER_COMMANDS`: um template de invocação por CLI
  (`codex exec --cd {worktree} --dangerously-bypass-approvals-and-sandbox
  ...`). Isso é o que roda de fato quando você é escolhido pra um job.
- **Importante, achado real de hoje**: esse mecanismo identifica qual
  *CLI/agente* despachar, nunca uma LLM específica dentro de um CLI. Os
  provedores de API crua provisionados pelo Pomerode (NVIDIA NIM,
  OpenRouter, Groq, Novita, Vercel AI Gateway, ...) **não** entram nesse
  pool -- eles são credenciais concedidas via `config/grants.json` +
  `grants.resolve_env`, usáveis hoje só via override explícito (ex.:
  `-m nvidia/openai/gpt-oss-20b` no comando do opencode). Ver PR #57
  (`factory-cauteloso`) pra prova real dessa composição e o porquê da
  premissa original (virar membro do pool) estar errada.
- `quota.py`: antes de despachar, checa se o candidato (`codex`/`gemini`)
  não está com cota estourada agora -- incidente real que motivou isso:
  2026-08-19, Codex e Agy reportaram `READY` mas já tinham estourado uso.

## Estado agora (2026-08-23, fim de tarde)

- **PRs abertas aguardando review do Thiago**: #56 e #90 (`AGENTS.md` em
  factory-cauteloso/mybagcenter-site), #57 (correção da issue #55 sobre
  provedores de capacidade), #58 (registro do nó `honda` que tinha ficado
  só local).
- **3 novos nós Tailscale**: colaboradores externos (`castilhoskalleb`,
  `filarrozcomovo`, `eduborgesschmeier`) conectaram máquinas Windows
  pessoais na rede. Instruções de onboarding SSH já enviadas por email,
  aguardando resposta -- ainda não são nós ativos de capacidade.
- **`honda`** (mini-PC Intel i5-8500, Ubuntu) voltou a responder depois
  de ficar offline por queda de energia.
- **Você (`poc-airflow`)**: sessão permanente rodando o PoC do Airflow --
  pelo que vi no seu terminal, você já absorveu bastante da filosofia do
  James por conta própria (bom sinal, é exatamente isso que o `AGENTS.md`
  pede).

## Onde ler mais (nessa ordem, se quiser aprofundar)

1. `AGENTS.md` (aqui neste repo, já escrito, só falta você decidir
   commitar).
2. `factory-cauteloso/CLAUDE.md` -> `factory-cauteloso/FACTORY.md` --
   doutrina "O que é a Factory" do Thiago, 17 princípios operacionais.
3. `factory-cauteloso/docs/james-philosophy.md` -- espelho da filosofia
   mais abstrata (reversão de entropia, "P=NP" operacional, "O(n)→O(1)").
4. `factory-cauteloso/README.md` -- arquitetura e convenções operacionais
   completas.
5. `bug-learning-loop` e `compactacao` -- antes de re-investigar algo do
   zero.

Qualquer dúvida real depois disso: pergunta pro Thiago direto, não
adivinha -- pedido explícito dele.

-- Claude (sessão `factory-cauteloso`), 2026-08-23
