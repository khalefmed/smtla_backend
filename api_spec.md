# SMTLA REST API Specification

## Base URL
`/api/`

## Authentication
This API is secured using **JSON Web Tokens (JWT)**.
Include the token in the HTTP `Authorization` header for all protected requests:
```http
Authorization: Bearer <your_access_token>
```

### Auth Endpoints
*   **POST** `/api/token/` - Obtain a pair of access and refresh tokens.
*   **POST** `/api/token/refresh/` - Exchange a refresh token for a new access token.

---

## Models & Endpoints

*Note: Endpoint paths (e.g., `/clients/`) assume standard Django REST Framework `DefaultRouter` naming conventions.*

### 1. Utilisateurs (Users)
**Endpoints:** `/api/utilisateurs/`

**Schema:**
```json
{
  "id": "integer (read-only)",
  "username": "string (required, unique)",
  "email": "string (email format)",
  "prenom": "string",
  "nom": "string",
  "telephone": "string",
  "type": "string (enum: 'directeur_operations', 'comptable', 'agent_port', 'directeur_general', 'assistant')",
  "is_active": "boolean",
  "is_staff": "boolean",
  "date_joined": "datetime (ISO 8601, read-only)"
}
```

---

### 2. Clients
**Endpoints:** `/api/clients/`

**Schema:**
```json
{
  "id": "integer (read-only)",
  "nom": "string (required)",
  "telephone": "string",
  "email": "string (email format)",
  "adresse": "string",
  "nif": "string"
}
```

---

### 3. Type de Matériel
**Endpoints:** `/api/type-materiels/`

**Schema:**
```json
{
  "id": "integer (read-only)",
  "nom": "string (required)",
  "description": "string",
  "date_creation": "datetime (ISO 8601, read-only)"
}
```

---

### 4. Rotation Entrante
**Endpoints:** `/api/rotation-entrantes/`

**Schema:**
```json
{
  "id": "integer (read-only)",
  "client": "integer (Foreign Key to Client)",
  "type_materiel": "integer (Foreign Key to TypeMateriel)",
  "numero_bordereau": "string",
  "observation": "string",
  "date_arrivee": "datetime (ISO 8601)",
  "camion": "string",
  "navire": "string",
  "quantite": "integer",
  "status": "string (e.g., 'en_cours')",
  "date_creation": "datetime (ISO 8601, read-only)"
}
```

---

### 5. Expression de Besoin
**Endpoints:** `/api/expression-besoins/`

**Schema:**
```json
{
  "id": "integer (read-only)",
  "reference": "string (required, unique, e.g., 'EB001/2026')",
  "nom_demandeur": "string",
  "direction": "string (e.g., 'OPERATION')",
  "affectation": "string (e.g., 'SIEGE')",
  "client_beneficiaire": "integer (Foreign Key to Client, nullable)",
  "bl_awb": "string",
  "navire": "string",
  "eta": "datetime (ISO 8601)",
  "status": "string (e.g., 'valide')",
  "tva": "boolean",
  "devise": "string (e.g., 'MRU')",
  "createur": "integer (Foreign Key to Utilisateur)",
  "valideur": "integer (Foreign Key to Utilisateur, nullable)",
  "date_creation": "datetime (ISO 8601, read-only)",
  "date_validation": "datetime (ISO 8601, nullable)"
}
```

---

### 6. Item Expression de Besoin
**Endpoints:** `/api/item-expression-besoins/`
*(Note: Can also be handled via nested serializers inside the `Expression de Besoin` endpoint)*

**Schema:**
```json
{
  "id": "integer (read-only)",
  "expression_besoin": "integer (Foreign Key to ExpressionBesoin, required)",
  "libelle": "string (required, e.g., 'AVANCE SUR SALAIRE')",
  "type": "string (e.g., 'avance_salaire')",
  "montant": "decimal (string format, e.g., '1000.00')"
}
```

---

## Common Operations
For each of the models listed above (except where restricted), the following HTTP methods are available:

| Method | Path | Description |
| :--- | :--- | :--- |
| **GET** | `/api/<resource>/` | List all items (supports pagination, filtering, and ordering). |
| **POST** | `/api/<resource>/` | Create a new item. |
| **GET** | `/api/<resource>/{id}/` | Retrieve a specific item by its ID. |
| **PUT** | `/api/<resource>/{id}/` | Update an entire item. |
| **PATCH** | `/api/<resource>/{id}/` | Partially update an item. |
| **DELETE** | `/api/<resource>/{id}/` | Delete an item. |

## Error Handling
Standard DRF HTTP status codes apply:
- `200 OK` / `201 Created` / `204 No Content`: Successful requests.
- `400 Bad Request`: Validation errors (payload missing required fields or invalid data types).
- `401 Unauthorized`: Missing or invalid JWT token.
- `403 Forbidden`: Authenticated, but lacking sufficient permissions.
- `404 Not Found`: Resource ID does not exist.
