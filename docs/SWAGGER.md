<img src="/static/images/logo.png" alt="Logo" class="img-fluid" style="height: 50px;" />

# SMARTX X-BRIDGE

**Versão:** 9.5.0

[**HOME**](/) | [**LOGS**](/logs) | [**API DOCS**](/docs)

SMARTX X-BRIDGE é uma plataforma de gestão de dispositivos RFID orientada para alto desempenho, integração com sistemas externos e operação em tempo real.

---

## Visão geral da API

Esta página traz uma visão geral dos grupos de endpoints expostos pela aplicação. A documentação interativa (Swagger UI) gerada automaticamente pelo FastAPI está disponível em `/docs` e inclui esquemas, tipos e exemplos. Aqui mantemos apenas um panorama sem exemplos de payloads.

Ambiente local padrão: `http://localhost:5000`

---

## Acessando a documentação interativa

- Swagger UI: `/docs` — interface interativa para explorar e testar endpoints.
- ReDoc: `/redoc` — documentação orientada à leitura.

> A documentação automática é gerada a partir dos roteadores em `app/routers/api/v1` e dos schemas Pydantic.

---

## Base da API

- Prefixo base: `/api/v1`
- Host padrão: `0.0.0.0` (executando localmente)
- Porta: configurada em `config/config.json` (padrão `5000`)

---

## Grupos de API

- **RFID** — `/api/v1/rfid`
  - Operações de leitura e consulta de tags em memória: listagem, estatísticas (GTIN), leitura de EPC/TID, limpeza de memória e escrita de EPC.

- **Devices** — `/api/v1/devices`
  - Gerenciamento dos leitores registrados: listagem, visualização e atualização de configurações por dispositivo, status e informações de conexão.

- **Application** — `/api/v1/application`
  - Endpoints para gerenciar configurações da aplicação, arquivos de configuração de dispositivos, checar alterações não salvas e operações de controle (restart/shutdown).

- **Simulator** — `/api/v1/simulator`
  - Injeção de dados sintéticos (tags, batches, eventos) e geração de GTIN‑14 para testes e demonstrações sem hardware.

- **Receive** — `/api/v1/receive`
  - Recepção de eventos enviados por leitores externos ou integrações (formatos genéricos e específicos de dispositivo).

- **License** — `/api/v1/license`
  - Recuperar informações de licença e enviar/atualizar a licença.

- **Controller** — `/api/v1/controller`
  - Informações de runtime sobre a instância do controlador RFID e seu estado operacional.

---

## Integrações e dispatchers

- Webhook: encaminhamento via HTTP POST com retry (configurável).
- XTRACK: integração dedicada com servidor XTRACK.
- Banco de dados: persistência via SQLAlchemy (SQLite/MySQL/Postgres).
- Arquivos de configuração de dispatchers: `config/dispatchers/` (exemplos em `examples/dispatchers/`).

---

## Observações

- Esta é uma visão geral; para detalhes (schemas, validação, exemplos) use `/docs`.
- Autenticação, permissões e middlewares podem ser aplicados a alguns endpoints — verifique `app/routers` e `app/core/middleware.py` quando necessário.
- Mantenha `pyproject.toml`, `docs/version.txt` e o `README.md` sincronizados com a versão do projeto.

---
