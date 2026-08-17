"""Koçluk Kuralları MCP Server — domain prensipleri ve rubric'i sunar."""
from pathlib import Path
from mcp.server.mcpserver import MCPServer

DOCS_DIR = Path(__file__).parent.parent.parent / "docs"

mcp = MCPServer("coach-rules")


def _read(name: str) -> str:
    return (DOCS_DIR / name).read_text(encoding="utf-8")


@mcp.resource("coach://principles")
def coach_principles() -> str:
    """Zone 2 disiplini, shin yönetimi, deload, yük yönetimi kuralları."""
    return _read("coach-principles.md")


@mcp.resource("coach://pain-rubric")
def pain_rubric() -> str:
    """0-10 ağrı ölçeği ve context yorumlaması."""
    return _read("pain-rubric.md")


@mcp.prompt()
def coach_assessment(user_message: str) -> str:
    """Kullanıcının hissiyat/ağrı mesajını değerlendirmek için system prompt üretir."""
    principles = _read("coach-principles.md")
    rubric = _read("pain-rubric.md")
    return (
        "Sen bir koşu antrenörüsün. Aşağıdaki prensipler ve rubric'e göre "
        "kullanıcıyı değerlendir.\n\n"
        f"=== PRENSIPLER ===\n{principles}\n\n"
        f"=== AĞRI RUBRIC ===\n{rubric}\n\n"
        f"=== KULLANICI MESAJI ===\n{user_message}\n\n"
        "Değerlendirmeni empati + veri + 2-3 alternatif formatında ver."
    )


if __name__ == "__main__":
    mcp.run()
