"""Environment file manager for reading and updating .env.paper and .env.live files."""

from pathlib import Path
from typing import Dict


class EnvManager:
    """Manages environment files for paper and live trading modes."""

    def __init__(self, project_root: Path | None = None):
        """Initialize EnvManager with project root directory.

        Args:
            project_root: Path to project root. If None, uses current working directory.
        """
        self.project_root = project_root or Path.cwd()

    def get_env_file_path(self, mode: str) -> Path:
        """Get the path to the environment file for the given mode.

        Args:
            mode: Trading mode ('paper' or 'live').

        Returns:
            Path to the .env.{mode} file.
        """
        return self.project_root / f".env.{mode}"

    def read_env_file(self, mode: str) -> Dict[str, str]:
        """Read environment variables from .env.{mode} file.

        Args:
            mode: Trading mode ('paper' or 'live').

        Returns:
            Dictionary of environment key-value pairs.
        """
        env_file = self.get_env_file_path(mode)
        env_vars: Dict[str, str] = {}

        if not env_file.exists():
            return env_vars

        with open(env_file, "r") as f:
            for line in f:
                line = line.strip()
                # Skip empty lines and comments
                if not line or line.startswith("#"):
                    continue
                # Parse KEY=VALUE format
                if "=" in line:
                    key, value = line.split("=", 1)
                    env_vars[key.strip()] = value.strip()

        return env_vars

    def write_env_file(self, mode: str, env_vars: Dict[str, str]) -> None:
        """Write environment variables to .env.{mode} file.

        Args:
            mode: Trading mode ('paper' or 'live').
            env_vars: Dictionary of environment key-value pairs.
        """
        env_file = self.get_env_file_path(mode)

        # Create parent directories if they don't exist
        env_file.parent.mkdir(parents=True, exist_ok=True)

        with open(env_file, "w") as f:
            for key, value in env_vars.items():
                f.write(f"{key}={value}\n")

    def update_env_var(self, mode: str, key: str, value: str) -> None:
        """Update a single environment variable in .env.{mode} file.

        Args:
            mode: Trading mode ('paper' or 'live').
            key: Environment variable key.
            value: Environment variable value.
        """
        env_vars = self.read_env_file(mode)
        env_vars[key] = value
        self.write_env_file(mode, env_vars)

    def delete_env_var(self, mode: str, key: str) -> None:
        """Delete an environment variable from .env.{mode} file.

        Args:
            mode: Trading mode ('paper' or 'live').
            key: Environment variable key to delete.
        """
        env_vars = self.read_env_file(mode)
        if key in env_vars:
            del env_vars[key]
            self.write_env_file(mode, env_vars)

    def env_file_exists(self, mode: str) -> bool:
        """Check if the environment file exists for the given mode.

        Args:
            mode: Trading mode ('paper' or 'live').

        Returns:
            True if the file exists, False otherwise.
        """
        return self.get_env_file_path(mode).exists()

    def get_all_modes(self) -> list[str]:
        """Get list of all available trading modes.

        Returns:
            List of mode names ('paper', 'live').
        """
        return ["paper", "live"]
