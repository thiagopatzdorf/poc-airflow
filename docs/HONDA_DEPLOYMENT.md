# Implantacao na honda

## Estado inventariado em 2026-08-23

- HP EliteDesk 800 G4 SFF; Intel i5-8500, 6 cores/6 threads.
- 7 GiB RAM, 32 GiB swap, cerca de 97 GiB livres em `/home`.
- Ubuntu 26.04 LTS; Intel UHD 630; Tailscale `100.73.146.19`.
- SSH e Tailscale ativos/habilitados; node guard ativo e `linger=yes`.
- Docker ainda nao instalado; MicroK8s existe mas o usuario nao tem acesso.

## Passo humano privilegiado

O script abaixo e curto, auditavel e precisa ser executado pelo operador em terminal
interativo porque `patz` exige senha de sudo:

```bash
cd ~/poc-airflow
./scripts/prepare-honda.sh
```

Ele instala Docker/Compose dos repositorios Ubuntu, habilita Docker, adiciona `patz` ao
grupo e mascara suspensao/hibernacao. Revise antes de executar. Depois, encerre e reabra
a sessao e rode:

```bash
make init
make up
tailscale serve --bg 8080
make status
```

## Acesso

A interface escuta somente em `127.0.0.1:8080`. Tailscale Serve publica
`https://honda.tailf3785c.ts.net` exclusivamente na tailnet, com TLS gerenciado.
A politica de reautenticacao/MFA deve ser confirmada no IdP da tailnet; TLS e pertencer a
tailnet, sozinhos, nao provam que MFA esteja exigido.

## Rollback

```bash
make down
```

Isso para os containers e preserva o volume PostgreSQL. Nao use `docker compose down -v`
sem autorizacao, pois essa opcao remove os dados persistidos.

## Release e deploy auditável

O workflow release-candidate-and-deploy empacota tags v* e execuções manuais. Ele repete testes e análise estática, constrói e escaneia a imagem, e publica fonte, manifesto, checksums, SBOM SPDX e atestação. Tags geram evidência, mas não fazem deploy automaticamente.

Deploy exige workflow_dispatch com deploy_honda=true, aprovação no GitHub Environment production-honda e runner auto-hospedado com labels self-hosted, linux, x64, honda e poc-airflow. Configure reviewer obrigatório, impeça autoaprovação quando disponível e proteja main. O runner usa o .env já existente na Honda; segredos nunca são inputs. Pertencer ao grupo Docker equivale praticamente a root, portanto esse runner deve ser dedicado e restrito ao repositório privado.

O script scripts/deploy-honda.sh exige SHA completa igual ao checkout, serializa implantações com flock, salva snapshot imutável por commit e promove somente código/configuração. Ele preserva .env, credenciais geradas, logs, dados e volumes nomeados. Antes de confirmar, valida Compose, constrói, migra, sobe, verifica health e exige zero erro de importação das DAGs. Falha volta automaticamente ao último snapshot confirmado.

A ativação operacional ainda requer criar o Environment protegido e instalar o runner dedicado na Honda. Até isso ocorrer, o job fica enfileirado e nenhum deploy automático é alegado. Migrações de banco podem ser forward-only: rollback volta código e containers, não schema ou dados. Mudanças incompatíveis exigem backup/restauração testados antes da promoção.
