"""
Script para fazer pull de prompts do LangSmith Prompt Hub.

Este script:
1. Conecta ao LangSmith usando credenciais do .env
2. Faz pull dos prompts do Hub
3. Salva localmente em prompts/bug_to_user_story_v1.yml

SIMPLIFICADO: Usa serialização nativa do LangChain para extrair prompts.
"""

import os
import sys
from dotenv import load_dotenv
from langchain import hub
from utils import save_yaml, check_env_vars, print_section_header

load_dotenv()


def pull_prompts_from_langsmith():
    prompt = hub.pull("leonanluppi/bug_to_user_story_v1")

    prompt_data = {
        "bug_to_user_story_v1": {
            "description": "Prompt para converter relatos de bugs em User Stories",
            "system_prompt": prompt.messages[0].prompt.template,
            "user_prompt": prompt.messages[1].prompt.template,
            "version": "v1",
        }
    }

    save_yaml(prompt_data, "prompts/bug_to_user_story_v1.yml")
    print("✓ Prompt salvo em prompts/bug_to_user_story_v1.yml")



def main():
    """Função principal"""
    print_section_header("Pulling Prompts from LangSmith Hub")
    check_env_vars(["LANGSMITH_API_KEY"])
    pull_prompts_from_langsmith()
    print("Prompts pulled successfully!")


if __name__ == "__main__":
    sys.exit(main())
