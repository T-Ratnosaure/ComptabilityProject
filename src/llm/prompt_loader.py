"""Prompt loader for managing system prompts and templates."""

import json
from pathlib import Path
from typing import Any

from cachetools import TTLCache
from jinja2 import Environment, FileSystemLoader, select_autoescape

from src.llm.exceptions import LLMConfigurationError


class PromptLoader:
    """Load and manage system prompts with caching."""

    def __init__(self, prompts_dir: str | Path = "prompts"):
        """Initialize prompt loader.

        Args:
            prompts_dir: Path to prompts directory
        """
        self.prompts_dir = Path(prompts_dir)
        if not self.prompts_dir.exists():
            raise LLMConfigurationError(
                f"Prompts directory not found: {self.prompts_dir}"
            )

        # Cache with 1-hour TTL (prompts rarely change)
        self._cache: TTLCache = TTLCache(maxsize=50, ttl=3600)

        # Jinja2 environment for templates
        templates_dir = self.prompts_dir / "templates"
        if templates_dir.exists():
            self.jinja_env = Environment(
                loader=FileSystemLoader(templates_dir),
                autoescape=select_autoescape(),
                trim_blocks=True,
                lstrip_blocks=True,
            )
        else:
            self.jinja_env = None

        # Load metadata
        metadata_path = self.prompts_dir / "metadata.json"
        if metadata_path.exists():
            with open(metadata_path, encoding="utf-8") as f:
                self.metadata = json.load(f)
        else:
            self.metadata = {}

    def load_system_prompt(self, variant: str = "default") -> str:
        """Load complete system prompt.

        Args:
            variant: Prompt variant (default, concise, detailed)

        Returns:
            Combined system prompt

        Raises:
            LLMConfigurationError: If prompt files not found
        """
        cache_key = f"system_{variant}"
        if cache_key in self._cache:
            return self._cache[cache_key]

        # Load base components
        base = self._load_file("system/base.md")
        tax_expert = self._load_file("system/tax_expert.md")
        safety = self._load_file("system/safety.md")

        # Combine prompts
        system_prompt = f"{base}\n\n{tax_expert}\n\n{safety}"

        # Cache and return
        self._cache[cache_key] = system_prompt
        return system_prompt

    def load_few_shot_examples(self, category: str) -> str:
        """Load few-shot examples for a category.

        Args:
            category: Example category (per, regime, etc.)

        Returns:
            Few-shot examples markdown

        Raises:
            LLMConfigurationError: If examples file not found
        """
        cache_key = f"examples_{category}"
        if cache_key in self._cache:
            return self._cache[cache_key]

        # Load examples file
        examples_file = f"examples/few_shot_{category}.md"
        examples = self._load_file(examples_file)

        # Cache and return
        self._cache[cache_key] = examples
        return examples

    def render_template(self, template_name: str, **variables: Any) -> str:
        """Render Jinja2 template with variables.

        Args:
            template_name: Template filename (e.g., "analysis_request.jinja2")
            **variables: Template variables

        Returns:
            Rendered template

        Raises:
            LLMConfigurationError: If template not found or Jinja2 not configured
        """
        if not self.jinja_env:
            raise LLMConfigurationError(
                "Templates directory not found, Jinja2 not configured"
            )

        try:
            template = self.jinja_env.get_template(template_name)
            return template.render(**variables)
        except Exception as e:
            raise LLMConfigurationError(
                f"Failed to render template {template_name}: {e}"
            ) from e

    def get_metadata(self, key: str | None = None) -> Any:
        """Get prompt metadata.

        Args:
            key: Metadata key (None for all metadata)

        Returns:
            Metadata value or full metadata dict
        """
        if key is None:
            return self.metadata
        return self.metadata.get(key)

    def _load_file(self, relative_path: str) -> str:
        """Load prompt file content.

        Args:
            relative_path: Path relative to prompts_dir

        Returns:
            File content

        Raises:
            LLMConfigurationError: If file not found
        """
        file_path = self.prompts_dir / relative_path
        if not file_path.exists():
            raise LLMConfigurationError(f"Prompt file not found: {file_path}")

        try:
            with open(file_path, encoding="utf-8") as f:
                return f.read()
        except Exception as e:
            raise LLMConfigurationError(
                f"Failed to read prompt file {file_path}: {e}"
            ) from e

    def clear_cache(self) -> None:
        """Clear prompt cache (useful for testing or prompt updates)."""
        self._cache.clear()
