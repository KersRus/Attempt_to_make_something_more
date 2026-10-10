def analyze_news(news_items: list[dict]) -> str:
    """
    Форматирует список новостей в читаемый текст для ntfy.
    Никакого AI — фильтрация по компаниям уже сделана в news_fetcher.py.
    """
    if not news_items:
        return ""

    # Убираем дубли по заголовку
    seen = set()
    unique = []
    for item in news_items:
        title = item.get("title", "").strip()
        if title and title not in seen:
            seen.add(title)
            unique.append(item)

    if not unique:
        return ""

    lines = []
    for item in unique[:15]:
        source = item.get("source", "")
        title = item.get("title", "")
        lines.append(f"• [{source}] {title}")

    return "\n".join(lines)
