# Asana Security Checks

Complete implementation of Asana security checks assignment with three parts:
1. **Part 1**: API Research & Endpoint Mapping
2. **Part 2**: Data Fetcher (consolidated JSON)
3. **Part 3**: JSONata Security Checks

This repository contains both the original monolithic implementation (`asana_data_extractor.py`) and the new modular implementation (`asana-security-checks/`).

## Возможности

- Получение списка пользователей workspace (администраторы и внешние пользователи)
- Получение списка проектов с полями `archived` и `modified_at`
- Объединение всех данных в один JSON файл
- Детальная статистика извлеченных данных
- **Проверки безопасности:**
  - Проверка количества администраторов (не более 4)
  - Проверка неактивных проектов (не изменялись более 365 дней)
  - Проверка активных внешних пользователей
- Генерация отчета по безопасности

## Assignment Parts

### Part 1 — API Research & Endpoint Mapping
- **Documentation**: `asana-security-checks/docs/API_MAPPING.md`
- **Status**: ✅ Complete
- **Description**: Comprehensive mapping of Asana REST API endpoints to security checks

### Part 2 — Data Fetcher
- **Implementation**: `asana-security-checks/src/fetcher/`
- **Runner**: `fetch_consolidated.py`
- **Output**: `asana-security-checks/data/consolidated.json`
- **Status**: ✅ Complete

### Part 3 — JSONata Security Checks
- **Implementation**: `asana-security-checks/src/checks/`
- **Runner**: `run_checks.py`
- **Output**: `asana-security-checks/data/checks_result.json`
- **Status**: ✅ Complete

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Set up authentication:
   - Option A: Set environment variable `ASANA_PAT=your_token_here`
   - Option B: Create `token.txt` file with your Personal Access Token
   - ⚠️ **Security**: `token.txt` is already in `.gitignore`

## Usage

### Original Implementation (Monolithic)
```bash
python3 asana_data_extractor.py
```

### New Modular Implementation

#### Part 2: Fetch Data
```bash
python3 fetch_consolidated.py
```
- Output: `asana-security-checks/data/consolidated.json`

#### Part 3: Run Security Checks
```bash
python3 run_checks.py
```
- Output: `asana-security-checks/data/checks_result.json`

### Both Steps Together
```bash
python3 fetch_consolidated.py && python3 run_checks.py
```

## Results from Single Run

### Part 2 Output (consolidated.json)
```json
{
  "workspace": {
    "gid": "1211487110823678",
    "resource_type": "workspace",
    "name": "My workspace"
  },
  "users": [
    {
      "gid": "1211487110823666",
      "email": "advahov22vadim@gmail.com",
      "name": "Vadim Advahov",
      "resource_type": "user"
    },
    {
      "gid": "1211487111272383",
      "email": "vadim.advahov@isa.utm.md",
      "name": "vadim.advahov@isa.utm.md",
      "resource_type": "user"
    }
  ],
  "projects": [
    {
      "gid": "1211486774855874",
      "archived": false,
      "color": "aqua",
      "created_at": "2025-09-28T07:09:53.773Z",
      "modified_at": "2025-09-28T07:09:54.551Z",
      "name": "Vadim's first project",
      "notes": "",
      "owner": {
        "gid": "1211487110823666",
        "resource_type": "user"
      },
      "permalink_url": "https://app.asana.com/1/1211487110823678/project/1211486774855874",
      "public": false,
      "team": {
        "gid": "1211487110823680",
        "resource_type": "team"
      }
    }
  ],
  "extracted_at": "2025-09-28T11:24:36.151912"
}
```

### Part 3 Output (checks_result.json)
```json
{
  "admin_count_check": {
    "description": "No more than 4 Admins Configured",
    "result": {
      "admin_count": 0,
      "is_violation": false
    }
  },
  "inactive_projects_check": {
    "description": "No Inactive Projects Present (365+ days, not archived)",
    "result": {
      "inactive_projects": [],
      "inactive_count": 0,
      "is_violation": false
    }
  },
  "external_users_check": {
    "description": "No Active External Users",
    "result": {
      "external_users": [
        {
          "gid": "1211487110823666",
          "name": "Vadim Advahov",
          "email": "advahov22vadim@gmail.com"
        },
        {
          "gid": "1211487111272383",
          "name": "vadim.advahov@isa.utm.md",
          "email": "vadim.advahov@isa.utm.md"
        }
      ],
      "external_count": 2,
      "is_violation": true
    }
  }
}
```

### Security Check Summary
- ✅ **Admin Count**: 0 admins (PASS - within limit of 4)
- ✅ **Inactive Projects**: 0 inactive projects (PASS - no projects older than 365 days)
- ❌ **External Users**: 2 external users (VIOLATION - external users detected)

## Documentation

- **Implementation Details**: See `IMPLEMENTATION.md` for detailed explanation of each part
- **API Mapping**: See `asana-security-checks/docs/API_MAPPING.md` for Part 1 documentation

## Структура выходного JSON

```json
{
  "workspace": {
    "gid": "workspace_id",
    "name": "Workspace Name"
  },
  "users": {
    "admins": [...],
    "external_users": [...]
  },
  "projects": [...],
  "extracted_at": "2024-01-01T12:00:00",
  "total_admins": 5,
  "total_external_users": 10,
  "total_projects": 15,
  "security_audit": {
    "total_checks": 3,
    "violations": 1,
    "passed": 2,
    "overall_status": "VIOLATIONS FOUND",
    "checks": {
      "admin_count": { "status": "PASS", "admin_count": 2 },
      "inactive_projects": { "status": "VIOLATION", "inactive_projects_count": 3 },
      "active_external_users": { "status": "PASS", "external_users_count": 0 }
    }
  }
}
```

## Получение Personal Access Token

1. Войдите в Asana
2. Перейдите в настройки профиля
3. Выберите "Apps" → "Personal Access Tokens"
4. Создайте новый токен
5. Скопируйте токен в файл `token.txt`

## Проверки безопасности

Скрипт выполняет три основные проверки безопасности:

### 1. Проверка количества администраторов
- **Цель**: Не более 4 администраторов в workspace
- **Статус**: ✅ PASS / ❌ VIOLATION
- **Детали**: Показывает текущее количество администраторов

### 2. Проверка неактивных проектов
- **Цель**: Отсутствие проектов, не изменявшихся более 365 дней
- **Статус**: ✅ PASS / ❌ VIOLATION
- **Детали**: Список неактивных проектов с количеством дней без изменений

### 3. Проверка внешних пользователей
- **Цель**: Отсутствие активных внешних (гостевых) пользователей
- **Статус**: ✅ PASS / ❌ VIOLATION
- **Детали**: Список всех внешних пользователей с доступом к данным

## Требования

- Python 3.6+
- Personal Access Token от Asana
- Доступ к интернету для API запросов
