"""
Script para fazer push de prompts otimizados ao LangSmith Prompt Hub.

Este script:
1. Lê os prompts otimizados de prompts/bug_to_user_story_v2.yml
2. Valida os prompts
3. Faz push PÚBLICO para o LangSmith Hub
4. Adiciona metadados (tags, descrição, técnicas utilizadas)

SIMPLIFICADO: Código mais limpo e direto ao ponto.
"""

import os
import sys
from dotenv import load_dotenv
from langchain_core.prompts import ChatPromptTemplate
from utils import load_yaml, check_env_vars, print_section_header, validate_prompt_structure
from langsmith import Client

load_dotenv()


def push_prompt_to_langsmith(prompt_name: str, prompt_data: dict) -> bool:
    """
    Faz push do prompt otimizado para o LangSmith Hub (PÚBLICO).

    Args:
        prompt_name: Nome do prompt
        prompt_data: Dados do prompt

    Returns:
        True se sucesso, False caso contrário
    """
    try:
        prompt_template = ChatPromptTemplate.from_messages([
            ("system", prompt_data["system_prompt"]),
            ("human", prompt_data["user_prompt"]),
        ])

        tags = prompt_data.get("tags", [])
        if isinstance(tags, str):
            tags = [tags]

        version = prompt_data.get("version")
        if version:
            tags.append(str(version))

        techniques = prompt_data.get("techniques_applied", [])
        if isinstance(techniques, str):
            techniques = [techniques]
        tags.extend(str(technique) for technique in techniques)

        client = Client()
        url = client.push_prompt(
            prompt_name,
            object=prompt_template,
            is_public=True,
            description=prompt_data.get("description"),
            tags=tags or None,
        )

        print(f"✓ Prompt publicado com sucesso: {url}")
        return True

    except Exception as e:
        print(f"Erro ao fazer push do prompt '{prompt_name}': {e}")
        return False


def validate_prompt(prompt_data: dict) -> tuple[bool, list]:
    """
    Valida estrutura básica de um prompt (versão simplificada).

    Args:
        prompt_data: Dados do prompt

    Returns:
        (is_valid, errors) - Tupla com status e lista de erros
    """
    is_valid, errors = validate_prompt_structure(prompt_data)

    user_prompt = prompt_data.get("user_prompt", "").strip()
    if not user_prompt:
        errors.append("user_prompt está vazio")

    if "TODO" in user_prompt:
        errors.append("user_prompt ainda contém TODOs")

    return (len(errors) == 0 and is_valid, errors)


def main():
    """Função principal"""
    print_section_header("Pushing Prompts to LangSmith Hub")

    if not check_env_vars(["LANGSMITH_API_KEY", "USERNAME_LANGSMITH_HUB"]):
        return 1

    prompts = load_yaml("prompts/bug_to_user_story_v2.yml")
    if not prompts:
        return 1

    username = os.getenv("USERNAME_LANGSMITH_HUB", "").strip()
    success = True

    for prompt_name, prompt_data in prompts.items():
        is_valid, errors = validate_prompt(prompt_data)

        if not is_valid:
            success = False
            print(f"Prompt inválido: {prompt_name}")
            for error in errors:
                print(f"   - {error}")
            continue

        print(f"Prompt válido: {prompt_name}")

        full_prompt_name = f"{username}/{prompt_name}"

        if not push_prompt_to_langsmith(full_prompt_name, prompt_data):
            success = False

    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
