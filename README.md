# myTrip-backend

API FastAPI do MyTrip. Esta seção lista todos os endpoints para facilitar a integração.

**Docs**
- Swagger UI: `/docs`
- ReDoc: `/redoc`
- OpenAPI JSON: `/openapi.json`

**Autenticação**
- Quase todos os endpoints exigem header `Authorization: Bearer <token>`.
- Aceita dois tipos de token:
  - Firebase ID Token (direto do Firebase Auth)
  - JWT interno (curto) obtido via `POST /auth/exchange` passando o Firebase ID Token no header Authorization

**Saúde/Meta**
- GET `/` — Mensagem simples de status (public)
- GET `/favicon.ico` — 204 (public)
- GET `/health` — Verifica conexão com DB (public)
- GET `/health/db` — Detalha conexão com DB (public)
- GET `/health/app` — Metadados de deploy/uptime/ambiente (public)

**Auth**
- POST `/auth/exchange` — Troca um Firebase ID Token por um JWT interno curto.
  - Header: `Authorization: Bearer <FIREBASE_ID_TOKEN>`
  - Resposta: `{ access_token, token_type, expires_in_min }`

**Usuários**
- GET `/users/me` — Retorna o usuário autenticado. (requer Bearer)
- PATCH `/users/me` — Atualiza campos do perfil: `name`, `photo_url`. (requer Bearer)
- DELETE `/users/me` — Desativa o usuário (marca `is_active = False`). (requer Bearer)

**Viagens (Trips)**
- GET `/trips` — Lista viagens do usuário (paginado e com filtros). (requer Bearer)
  - Query: `skip` (int, default 0), `limit` (1–200), `start_from` (date), `end_until` (date)
- GET `/trips/{trip_id}` — Detalhe de uma viagem do usuário. (requer Bearer)
- POST `/trips` — Cria viagem. (requer Bearer)
  - Body: `name` (str), `start_date` (date), `end_date` (date), `currency_code` (str, 3), `destination` (str, opcional), `total_budget` (float, opcional)
- PUT `/trips/{trip_id}` — Atualiza viagem (parcial). (requer Bearer)
  - Body (todos opcionais): `name`, `start_date`, `end_date`, `currency_code`, `destination`, `total_budget`
- DELETE `/trips/{trip_id}` — Exclui viagem do usuário. (requer Bearer)

**Categorias de Orçamento**
- GET `/budget-categories` — Lista categorias disponíveis (seedadas). (requer Bearer)

**Itens de Orçamento (por Viagem)**
- GET `/trips/{trip_id}/items` — Lista itens da viagem com filtros/paginação. (requer Bearer)
  - Query: `skip` (int, default 0), `limit` (1–500), `date_from` (date), `date_until` (date), `category_id` (int)
- GET `/trips/{trip_id}/items/{item_id}` — Detalhe de um item. (requer Bearer)
- POST `/trips/{trip_id}/items` — Cria item. (requer Bearer)
  - Body: `category_id` (int), `title` (str, opcional), `planned_amount` (float, opcional), `actual_amount` (float, opcional), `date` (date, opcional)
- PUT `/trips/{trip_id}/items/{item_id}` — Atualiza item (parcial). (requer Bearer)
  - Body (opcionais): `category_id`, `title`, `planned_amount`, `actual_amount`, `date`
- DELETE `/trips/{trip_id}/items/{item_id}` — Remove item. (requer Bearer)

**Metas de Orçamento por Categoria (por Viagem)**
- GET `/trips/{trip_id}/targets` — Lista metas por categoria da viagem. (requer Bearer)
- GET `/trips/{trip_id}/targets/{category_id}` — Detalhe da meta para a categoria. (requer Bearer)
- POST `/trips/{trip_id}/targets` — Upsert de meta por categoria. (requer Bearer)
  - Body: `category_id` (int), `planned_amount` (float)
- DELETE `/trips/{trip_id}/targets/{category_id}` — Remove meta da categoria. (requer Bearer)

Observações
- Todos os endpoints protegidos validam o usuário via `Authorization: Bearer` e garantem que recursos (viagens/itens/metas) pertençam ao usuário.
- Categorias de orçamento são somente leitura e vêm pre-populadas via migrations.

## Exemplos de Requisição

Use `Authorization: Bearer <TOKEN>` em todos os endpoints protegidos.

### Troca de token (Firebase -> JWT interno)

Request

```bash
curl -X POST \
  -H "Authorization: Bearer <FIREBASE_ID_TOKEN>" \
  http://localhost:8000/auth/exchange
```

Response

```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIs...",
  "token_type": "bearer",
  "expires_in_min": 60
}
```

### Usuário atual

```bash
curl -H "Authorization: Bearer <JWT_INTERNO_OU_FIREBASE>" \
  http://localhost:8000/users/me
```

```json
{
  "id": 1,
  "email": "user@email.com",
  "firebase_uid": "abcd1234",
  "is_active": true,
  "name": "Usuário",
  "photo_url": null
}
```

### Criar viagem

```bash
curl -X POST http://localhost:8000/trips \
  -H "Authorization: Bearer <JWT>" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Paris",
    "destination": "Paris, França",
    "start_date": "2025-03-10",
    "end_date": "2025-03-17",
    "currency_code": "EUR",
    "total_budget": 5000
  }'
```

```json
{
  "id": 10,
  "user_id": 1,
  "name": "Paris",
  "destination": "Paris, França",
  "start_date": "2025-03-10",
  "end_date": "2025-03-17",
  "currency_code": "EUR",
  "total_budget": 5000
}
```

### Listar viagens com filtros

```bash
curl -H "Authorization: Bearer <JWT>" \
  "http://localhost:8000/trips?skip=0&limit=20&start_from=2025-01-01&end_until=2025-12-31"
```

```json
[
  {
    "id": 10,
    "user_id": 1,
    "name": "Paris",
    "start_date": "2025-03-10",
    "end_date": "2025-03-17",
    "currency_code": "EUR",
    "total_budget": 5000
  }
]
```

### Listar categorias de orçamento

```bash
curl -H "Authorization: Bearer <JWT>" http://localhost:8000/budget-categories
```

```json
[
  { "id": 1, "key": "transport", "label": "Transporte" },
  { "id": 2, "key": "food", "label": "Alimentação" }
]
```

### Criar item de orçamento

```bash
curl -X POST http://localhost:8000/trips/10/items \
  -H "Authorization: Bearer <JWT>" \
  -H "Content-Type: application/json" \
  -d '{
    "category_id": 2,
    "title": "Jantar",
    "planned_amount": 120,
    "actual_amount": 110,
    "date": "2025-03-11"
  }'
```

```json
{
  "id": 55,
  "trip_id": 10,
  "category_id": 2,
  "title": "Jantar",
  "planned_amount": 120.0,
  "actual_amount": 110.0,
  "date": "2025-03-11"
}
```

### Listar itens de orçamento com filtros

```bash
curl -H "Authorization: Bearer <JWT>" \
  "http://localhost:8000/trips/10/items?date_from=2025-03-10&date_until=2025-03-17&category_id=2&skip=0&limit=50"
```

```json
[
  {
    "id": 55,
    "trip_id": 10,
    "category_id": 2,
    "title": "Jantar",
    "planned_amount": 120.0,
    "actual_amount": 110.0,
    "date": "2025-03-11"
  }
]
```

### Upsert de meta por categoria

```bash
curl -X POST http://localhost:8000/trips/10/targets \
  -H "Authorization: Bearer <JWT>" \
  -H "Content-Type: application/json" \
  -d '{
    "category_id": 2,
    "planned_amount": 800
  }'
```

```json
{
  "id": 7,
  "trip_id": 10,
  "category_id": 2,
  "planned_amount": 800.0
}
```

### Obter meta por categoria

```bash
curl -H "Authorization: Bearer <JWT>" http://localhost:8000/trips/10/targets/2
```

```json
{
  "id": 7,
  "trip_id": 10,
  "category_id": 2,
  "planned_amount": 800.0
}
```

### Atualizar viagem

```bash
curl -X PUT http://localhost:8000/trips/10 \
  -H "Authorization: Bearer <JWT>" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Paris & Londres",
    "destination": "Paris, França; Londres, Reino Unido",
    "total_budget": 6500
  }'
```

```json
{
  "id": 10,
  "user_id": 1,
  "name": "Paris & Londres",
  "destination": "Paris, França; Londres, Reino Unido",
  "start_date": "2025-03-10",
  "end_date": "2025-03-17",
  "currency_code": "EUR",
  "total_budget": 6500
}
```

### Deletar viagem

```bash
curl -X DELETE -H "Authorization: Bearer <JWT>" \
  http://localhost:8000/trips/10 -i
```

Resposta esperada: `HTTP/1.1 204 No Content`

### Atualizar item de orçamento

```bash
curl -X PUT http://localhost:8000/trips/10/items/55 \
  -H "Authorization: Bearer <JWT>" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Jantar especial",
    "actual_amount": 115
  }'
```

```json
{
  "id": 55,
  "trip_id": 10,
  "category_id": 2,
  "title": "Jantar especial",
  "planned_amount": 120.0,
  "actual_amount": 115.0,
  "date": "2025-03-11"
}
```

### Deletar item de orçamento

```bash
curl -X DELETE -H "Authorization: Bearer <JWT>" \
  http://localhost:8000/trips/10/items/55 -i
```

Resposta esperada: `HTTP/1.1 204 No Content`

### Atualizar meta por categoria (upsert)

```bash
curl -X POST http://localhost:8000/trips/10/targets \
  -H "Authorization: Bearer <JWT>" \
  -H "Content-Type: application/json" \
  -d '{
    "category_id": 2,
    "planned_amount": 900
  }'
```

```json
{
  "id": 7,
  "trip_id": 10,
  "category_id": 2,
  "planned_amount": 900.0
}
```

### Deletar meta por categoria

```bash
curl -X DELETE -H "Authorization: Bearer <JWT>" \
  http://localhost:8000/trips/10/targets/2 -i
```

Resposta esperada: `HTTP/1.1 204 No Content`
