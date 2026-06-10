"""
Testes automatizados para validação de prompts.
"""
import pytest
import yaml
import sys
import re
from pathlib import Path

# Adicionar src ao path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from utils import validate_prompt_structure

PROJECT_ROOT = Path(__file__).parent.parent
PROMPTS_FILE = PROJECT_ROOT / "prompts" / "bug_to_user_story_v2.yml"
PROMPT_TEXT_FIELDS = ("system_prompt", "user_prompt")


def load_prompts(file_path: str):
    """Carrega prompts do arquivo YAML."""
    with open(file_path, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)


@pytest.fixture(scope="class")
def prompts():
    """Carrega todos os prompts otimizados que devem ser validados."""
    loaded_prompts = load_prompts(str(PROMPTS_FILE))
    assert isinstance(loaded_prompts, dict) and loaded_prompts, (
        f"Arquivo de prompts vazio ou inválido: {PROMPTS_FILE}"
    )
    return loaded_prompts


def prompt_text(prompt_data: dict) -> str:
    """Concatena campos textuais do prompt para validações de conteúdo."""
    return "\n".join(str(prompt_data.get(field, "")) for field in PROMPT_TEXT_FIELDS)


class TestPrompts:
    def test_prompt_has_system_prompt(self, prompts):
        """Verifica se o campo 'system_prompt' existe e não está vazio."""
        for prompt_name, prompt_data in prompts.items():
            assert "system_prompt" in prompt_data, (
                f"Prompt '{prompt_name}' não possui o campo 'system_prompt'."
            )
            assert prompt_data["system_prompt"].strip(), (
                f"Prompt '{prompt_name}' possui 'system_prompt' vazio."
            )

    def test_prompt_has_role_definition(self, prompts):
        """Verifica se o prompt define uma persona (ex: "Você é um Product Manager")."""
        role_patterns = [
            r"\bvoc[eê]\s+[ée]\b",
            r"\bvoc[eê]\s+atua\b",
            r"\bvoc[eê]\s+trabalha\b",
            r"\bvoc[eê]\s+transforma\b",
            r"\baja\s+como\b",
            r"\bassuma\s+o\s+papel\b",
            r"\bseja\s+um[a]?\b",
        ]

        for prompt_name, prompt_data in prompts.items():
            system_prompt = prompt_data.get("system_prompt", "")
            assert any(re.search(pattern, system_prompt, re.IGNORECASE) for pattern in role_patterns), (
                f"Prompt '{prompt_name}' deve definir claramente uma persona ou papel no system_prompt."
            )

    def test_prompt_mentions_format(self, prompts):
        """Verifica se o prompt exige formato Markdown ou User Story padrão."""
        for prompt_name, prompt_data in prompts.items():
            system_prompt = prompt_data.get("system_prompt", "")
            has_markdown_format = re.search(r"\bmarkdown\b", system_prompt, re.IGNORECASE)
            has_user_story_format = re.search(r"\b(user story|hist[oó]ria de usu[aá]rio)\b", system_prompt, re.IGNORECASE)
            has_acceptance_criteria = re.search(r"\bcrit[eé]rios de aceita[cç][aã]o\b", system_prompt, re.IGNORECASE)

            assert has_markdown_format or (has_user_story_format and has_acceptance_criteria), (
                f"Prompt '{prompt_name}' deve exigir Markdown ou formato padrão de User Story."
            )

    def test_prompt_has_few_shot_examples(self, prompts):
        """Verifica se o prompt contém exemplos de entrada/saída (técnica Few-shot)."""
        for prompt_name, prompt_data in prompts.items():
            text = prompt_text(prompt_data)
            has_examples_section = re.search(r"\bexemplos?\b", text, re.IGNORECASE)
            has_input_example = re.search(r"\b(entrada|input)\s*:", text, re.IGNORECASE)
            has_output_example = re.search(r"\b(sa[ií]da|output)\s*:", text, re.IGNORECASE)

            assert has_examples_section and has_input_example and has_output_example, (
                f"Prompt '{prompt_name}' deve conter exemplos Few-shot com entrada e saída."
            )

    def test_prompt_no_todos(self, prompts):
        """Garante que você não esqueceu nenhum `[TODO]` no texto."""
        for prompt_name, prompt_data in prompts.items():
            text = prompt_text(prompt_data)
            assert not re.search(r"\[todo\]|\btodo\b", text, re.IGNORECASE), (
                f"Prompt '{prompt_name}' ainda contém TODO no texto."
            )

    def test_minimum_techniques(self, prompts):
        """Verifica (através dos metadados do yaml) se pelo menos 2 técnicas foram listadas."""
        for prompt_name, prompt_data in prompts.items():
            is_valid, errors = validate_prompt_structure(prompt_data)
            techniques = prompt_data.get("techniques_applied", [])

            assert isinstance(techniques, list), (
                f"Prompt '{prompt_name}' deve declarar 'techniques_applied' como lista."
            )
            assert len(techniques) >= 2, (
                f"Prompt '{prompt_name}' deve listar pelo menos 2 técnicas aplicadas."
            )
            assert is_valid, (
                f"Prompt '{prompt_name}' falhou na validação estrutural: {errors}"
            )

if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
