# poc-airflow — AGENTS.md

## Conhecimento coletivo entre agentes (checar antes de re-investigar)

Nenhum agente com sessão permanente (Claude, Codex, Gemini, Qwen, Grok,
opencode, aider, ...) deveria pagar de novo por uma investigação que outro
já fez. Antes de gastar tokens re-derivando causa raiz de um bug ou
questionando se algo é ineficiente, procure primeiro em:

- `~/repos/bug-learning-loop` — bugs reais (qualquer projeto), causa raiz +
  fix + lição generalizável.
- `~/repos/compactacao` — casos reais de desperdício de recurso
  (tokens/memória/processamento/tempo) identificado ou corrigido, mais um
  checklist de perguntas em `principios.md`.

Se o achado for novo, registre nesses repos (não só na memória privada de
um agente) antes de seguir — é isso que faz o próximo agente (ou a próxima
sessão do mesmo agente) não redescobrir do zero.

## Sessão compartilhada por mais de uma pessoa: pausa antes de responder

Política do Thiago (2026-08-24), vale pra **todo agente**: antes de
responder, cheque se a sessão atual tem mais de uma pessoa/cliente ativo
ao mesmo tempo (`python3 ~/factory-cauteloso/bin/who-is-here.py` --
mostra "ATENÇÃO -- mais de um cliente" quando é o caso). Se for o caso,
espere uns 5 segundos antes de mandar a resposta -- dá tempo de reler a
última troca com calma e confirmar pra quem a resposta é destinada, em
vez de responder no automático pra pessoa errada só porque duas
conversas estão se misturando na mesma sessão.

Pra sessão tmux especificamente com esse risco,
`~/factory-cauteloso/bin/agent-lock.py claim tmux-session:<nome>
--agent-id <quem> --wait N` está disponível como fila real (só um
client "dono" por vez).

(Arquivo criado por outra sessão de agente enquanto o Codex estava com
commit pendente neste repo -- por isso ainda não foi commitado. Sem outras
instruções específicas deste projeto por enquanto; se este repo ganhar
convenções próprias, documente aqui.)

## Comunicação assíncrona com o Claude (mailbox, não teclado)

Se o Claude (ou qualquer outro agente permanente) precisar te passar uma
mensagem enquanto você está trabalhando, o canal certo é o mailbox
compartilhado (`bin/agent-mailbox.py`, repo `factory-cauteloso` --
script stdlib puro, sem depender do pacote Python do projeto, pensado
justamente pra qualquer CLI chamar direto), não digitar na sua sessão
tmux ao vivo. Isso existe porque digitar direto numa sessão interativa
sua no meio de uma ação (aprovação de comando pendente, etc.) já causou
problema real numa sessão anterior -- rascunho seu apagado sem querer.

Cheque suas mensagens de vez em quando (início de uma tarefa nova, ou em
qualquer pausa natural):

```bash
python3 /home/worker/factory-cauteloso/bin/agent-mailbox.py inbox --for codex
```

Pra responder ou avisar algo (ex.: "terminei X", "vou mexer em Y"):

```bash
python3 /home/worker/factory-cauteloso/bin/agent-mailbox.py send --to claude --from codex --message "..."
```

`--to broadcast` manda pra qualquer agente que checar (`inbox --all`
mostra o quadro geral de atividade). Mensagens ficam guardadas
indefinidamente (JSONL append-only) -- não tem "marcar como lida", então
não se assuste com histórico.
