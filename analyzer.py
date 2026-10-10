from rapidfuzz import fuzz


# Порог схожести. 0–100, где 100 — полное совпадение.
# 75 — хороший баланс: ловит перефразировки, но не схлопывает разные новости.
SIMILARITY_THRESHOLD = 75


def _normalize(title: str) -> str:
    """Приводит заголовок к нижнему регистру и убирает лишние символы."""
    title = title.lower()
    # Убираем пунктуацию, оставляя буквы, цифры и пробелы
    cleaned = "".join(c if c.isalnum() or c.isspace() else " " for c in title)
    # Схлопываем повторные пробелы
    return " ".join(cleaned.split())


def _deduplicate(news_items: list[dict]) -> list[dict]:
    """
    Убирает новости с похожими заголовками.
    Оставляет первую по времени (items приходят уже отсортированными).
    """
    unique = []
    for item in news_items:
        title_norm = _normalize(item.get("title", ""))
        if not title_norm:
            continue

        is_duplicate = False
        for kept in unique:
            kept_norm = _normalize(kept.get("title", ""))
            # token_set_ratio игнорирует порядок слов и повторы
            similarity = fuzz.token_set_ratio(title_norm, kept_norm)
            if similarity >= SIMILARITY_THRESHOLD:
                is_duplicate = True
                break

        if not is_duplicate:
            unique.append(item)

    return unique


def analyze_news(news_items: list[dict]) -> str:
    """
    Форматирует список новостей для ntfy,
    убирая дубликаты по схожести заголовков.
    """
    if not news_items:
        return ""

    # Сначала точные дубли по заголовку
    seen = set()
    exact_unique = []
    for item in news_items:
        title = item.get("title", "").strip()
        if title and title not in seen:
            seen.add(title)
            exact_unique.append(item)

    # Затем нечёткая дедупликация
    unique = _deduplicate(exact_unique)

    if not unique:
        return ""

    lines = []
    for item in unique[:15]:
        source = item.get("source", "")
        title = item.get("title", "")
        lines.append(f"• [{source}] {title}")

    return "\n".join(lines)
