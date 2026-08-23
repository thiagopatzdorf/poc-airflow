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
make status
```

## Acesso

A interface escuta somente em `100.73.146.19:8080`, portanto e alcancavel pela tailnet e
nao por `0.0.0.0`. Para a POC, o transporte Tailscale fornece criptografia de rede.
HTTPS, IdP e MFA corporativos continuam sendo gates obrigatorios para homologacao.

## Rollback

```bash
make down
```

Isso para os containers e preserva o volume PostgreSQL. Nao use `docker compose down -v`
sem autorizacao, pois essa opcao remove os dados persistidos.

