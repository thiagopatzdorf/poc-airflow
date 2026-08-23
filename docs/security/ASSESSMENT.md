# Evidencias para avaliacao independente

## Automatizado em todo push/PR

- testes unitarios e lint;
- Bandit e CodeQL para SAST;
- Gitleaks para segredos no historico;
- Trivy para dependencias, secrets, Docker e IaC;
- dependency review em pull requests;
- scan da imagem e resultado SARIF no GitHub Security;
- SBOM SPDX da imagem como artefato.

As actions sao referenciadas por SHA imutavel, com a tag documentada ao lado. O token da
CI usa permissoes minimas por job, checkout nao persiste credencial e jobs possuem timeout.

## Avaliacao humana ainda obrigatoria

- threat modeling com arquitetura e donos dos sistemas reais;
- pentest autenticado e nao autenticado;
- revisao das ACLs/device posture da tailnet;
- hardening CIS do host e runtime;
- aprovacao de LGPD, Bacen, retencao, continuidade e resposta a incidentes;
- teste de restauracao e evidencia off-host/WORM;
- SSO/MFA, segregacao de funcoes e recertificacao de acessos.

Resultados automaticos reduzem risco e produzem evidencia; nao constituem certificacao.

