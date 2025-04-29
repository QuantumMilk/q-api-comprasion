#!/bin/bash

# Скрипт для настройки CI/CD для проекта сравнения API
# Проверяет наличие всех необходимых директорий и файлов,
# создает их если они отсутствуют

set -e

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

log() {
  echo -e "${GREEN}$(date '+%Y-%m-%d %H:%M:%S') - $1${NC}"
}

warn() {
  echo -e "${YELLOW}$(date '+%Y-%m-%d %H:%M:%S') - ПРЕДУПРЕЖДЕНИЕ: $1${NC}"
}

error() {
  echo -e "${RED}$(date '+%Y-%m-%d %H:%M:%S') - ОШИБКА: $1${NC}"
  exit 1
}

check_command() {
  if ! command -v $1 &> /dev/null; then
    error "Команда '$1' не найдена. Пожалуйста, установите $2."
  fi
}

# Проверяем наличие необходимых команд
log "Проверка наличия необходимых зависимостей..."
check_command "git" "Git"
check_command "docker" "Docker"
check_command "docker-compose" "Docker Compose"

# Проверяем, что скрипт запущен из корневой директории проекта
if [ ! -f "docker-compose.yml" ]; then
  error "Скрипт должен быть запущен из корневой директории проекта, содержащей файл docker-compose.yml"
fi

# Создаем необходимые директории для CI/CD
log "Создание необходимых директорий для CI/CD..."
mkdir -p .github/workflows
mkdir -p .github/ci
mkdir -p tests/results/graphs

# Проверяем наличие необходимых файлов
log "Проверка наличия необходимых файлов для CI/CD..."

# Проверяем workflow файл
if [ ! -f ".github/workflows/api-comparison-workflow.yml" ]; then
  warn "Файл workflow не найден, копирую стандартный..."
  cp -n scripts/templates/api-comparison-workflow.yml .github/workflows/ 2>/dev/null || \
  warn "Шаблон workflow не найден. Убедитесь, что создан файл .github/workflows/api-comparison-workflow.yml"
else
  log "Файл workflow найден: .github/workflows/api-comparison-workflow.yml"
fi

# Проверяем скрипт инициализации базы данных
if [ ! -f ".github/ci/initialize-database.sh" ]; then
  warn "Скрипт инициализации базы данных не найден, копирую стандартный..."
  cp -n scripts/templates/initialize-database.sh .github/ci/ 2>/dev/null || \
  warn "Шаблон скрипта инициализации базы данных не найден. Убедитесь, что создан файл .github/ci/initialize-database.sh"
else
  log "Скрипт инициализации базы данных найден: .github/ci/initialize-database.sh"
fi

# Проверяем наличие тестовых скриптов
if [ ! -d "tests/k6-scripts" ]; then
  warn "Директория с k6-скриптами не найдена. Убедитесь, что создана директория tests/k6-scripts с необходимыми скриптами"
else
  log "Директория с k6-скриптами найдена: tests/k6-scripts"
fi

# Проверяем наличие скрипта генерации отчетов
if [ ! -f "tests/generate_report.py" ]; then
  warn "Скрипт генерации отчетов не найден. Убедитесь, что создан файл tests/generate_report.py"
else
  log "Скрипт генерации отчетов найден: tests/generate_report.py"
fi

# Проверяем наличие .env файла
if [ ! -f ".env" ]; then
  if [ -f ".env.example" ]; then
    warn ".env файл не найден, создаю из .env.example..."
    cp .env.example .env
  else
    warn ".env и .env.example файлы не найдены. Создайте файл .env с необходимыми переменными окружения"
  fi
else
  log ".env файл найден"
fi

# Проверяем репозиторий Git
if [ -d ".git" ]; then
  log "Git репозиторий найден"
  
  # Проверяем, настроен ли remote origin
  if git remote get-url origin &>/dev/null; then
    REPO_URL=$(git remote get-url origin)
    log "Remote origin настроен: $REPO_URL"
    
    # Извлекаем имя пользователя и репозитория для GitHub
    if [[ $REPO_URL == *"github.com"* ]]; then
      # Извлекаем имя пользователя/организации и репозитория из URL
      if [[ $REPO_URL =~ github.com[:/]([^/]+)/([^/.]+) ]]; then
        GITHUB_USERNAME=${BASH_REMATCH[1]}
        REPO_NAME=${BASH_REMATCH[2]}
        log "GitHub репозиторий: $GITHUB_USERNAME/$REPO_NAME"
        
        # Обновляем URL в README.md, если он существует
        if [ -f "README.md" ]; then
          sed -i "s|https://github.com/username/api-comparison|https://github.com/$GITHUB_USERNAME/$REPO_NAME|g" README.md 2>/dev/null || \
          warn "Не удалось обновить URL в README.md"
          
          sed -i "s|https://\[username\].github.io/api-comparison/|https://$GITHUB_USERNAME.github.io/$REPO_NAME/|g" README.md 2>/dev/null || \
          warn "Не удалось обновить URL GitHub Pages в README.md"
        fi
      else
        warn "Не удалось извлечь имя пользователя и репозитория из URL: $REPO_URL"
      fi
    else
      warn "Remote origin не является GitHub репозиторием: $REPO_URL"
    fi
  else
    warn "Remote origin не настроен. CI/CD требует настроенного GitHub репозитория."
  fi
else
  warn "Git репозиторий не найден. Инициализируйте Git репозиторий для использования CI/CD"
fi

log "Настройка CI/CD завершена. Убедитесь, что все предупреждения обработаны."
log "Для включения CI/CD в GitHub:"
log "1. Запушьте код в GitHub репозиторий"
log "2. Перейдите в Settings > Pages и выберите источником ветку gh-pages"
log "3. Перейдите в Actions и убедитесь, что workflow 'API Comparison CI/CD' активирован"