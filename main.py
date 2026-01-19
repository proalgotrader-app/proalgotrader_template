import os
import subprocess
import time
from pathlib import Path

import streamlit as st
from dotenv import load_dotenv

st.set_page_config(page_title="ProAlgoTrader", page_icon="📈", layout="wide")

# Initialize session state
if "is_running" not in st.session_state:
    st.session_state.is_running = False
if "mode" not in st.session_state:
    st.session_state.mode = "paper"
if "environment" not in st.session_state:
    st.session_state.environment = "development"
if "api_url" not in st.session_state:
    st.session_state.api_url = "https://proalgotrader_laravel.test"
if "logs" not in st.session_state:
    st.session_state.logs = []


def load_env_vars(mode: str) -> tuple[str, str]:
    """Load algo session key and secret from .env.{mode} file."""
    project_root = Path().cwd()
    env_file = project_root / f".env.{mode}"
    load_dotenv(env_file, override=True)
    key = os.getenv("ALGO_SESSION_KEY", "")
    secret = os.getenv("ALGO_SESSION_SECRET", "")
    return key, secret


def get_container_name(mode: str) -> str:
    """Generate container name based on mode."""
    return f"proalgotrader_{mode}"


def check_container_running(container_name: str) -> bool:
    """Check if container is currently running."""
    try:
        result = subprocess.run(
            ["docker", "inspect", "-f", "{{.State.Running}}", container_name],
            capture_output=True,
            text=True,
            timeout=5,
        )
        return result.stdout.strip() == "true"
    except Exception:
        return False


def start_docker_compose(
    mode: str, environment: str, api_url: str, key: str, secret: str
) -> str:
    """Start docker compose and return output."""
    env = os.environ.copy()
    env.update(
        {
            "MODE": mode,
            "ENVIRONMENT": environment,
            "API_URL": api_url,
            "ALGO_SESSION_KEY": key,
            "ALGO_SESSION_SECRET": secret,
            "CONTAINER_NAME": get_container_name(mode),
        }
    )

    result = subprocess.run(
        ["docker", "compose", "up", "--build", "-d"],
        cwd=Path(__file__).parent,
        env=env,
        capture_output=True,
        text=True,
        timeout=300,
    )

    output = result.stdout
    if result.stderr:
        output += "\n" + result.stderr

    if result.returncode != 0:
        raise Exception(output)

    return output


def stop_docker_compose(container_name: str) -> str:
    """Stop docker compose and return output."""
    result = subprocess.run(
        ["docker", "compose", "down"],
        cwd=Path(__file__).parent,
        env={"CONTAINER_NAME": container_name},
        capture_output=True,
        text=True,
        timeout=60,
    )

    output = result.stdout
    if result.stderr:
        output += "\n" + result.stderr

    return output


def get_all_logs(container_name: str) -> str:
    """Get all logs from docker container."""
    try:
        result = subprocess.run(
            ["docker", "logs", container_name],
            capture_output=True,
            text=True,
            timeout=10,
        )
        return result.stdout
    except Exception:
        return ""


# Sidebar - Settings
with st.sidebar:
    st.title("⚙️ Settings")

    mode = st.selectbox(
        "Trading Mode",
        ["paper", "live"],
        index=0 if st.session_state.mode != "live" else 1,
        disabled=st.session_state.is_running,
    )
    st.session_state.mode = mode

    environment = st.selectbox(
        "Environment",
        ["development", "production"],
        index=0 if st.session_state.environment != "production" else 1,
        disabled=st.session_state.is_running,
    )
    st.session_state.environment = environment

    api_url = st.text_input(
        "API URL",
        value=st.session_state.api_url,
        disabled=st.session_state.is_running,
    )
    st.session_state.api_url = api_url

    st.markdown("---")

    # Status
    container_name = get_container_name(mode)
    is_running = check_container_running(container_name)
    st.session_state.is_running = is_running

    if is_running:
        st.success(f"🟢 Running")
    else:
        st.info("⚪ Stopped")

    st.markdown("---")

    # Single button - Start or Stop
    key, secret = load_env_vars(mode)

    if is_running:
        if st.button("⏹️ Stop", use_container_width=True):
            with st.spinner("Stopping..."):
                try:
                    output = stop_docker_compose(container_name)
                    st.session_state.logs.append(
                        f"\n=== Docker Compose Stop ===\n{output}\n"
                    )
                    time.sleep(1)
                    st.rerun()
                except Exception as e:
                    st.error(f"Failed: {e}")
    else:
        if st.button("▶️ Start", type="primary", use_container_width=True):
            if not key or not secret:
                st.error(f"❌ No `.env.{mode}` file found")
            else:
                with st.spinner("Starting..."):
                    try:
                        output = start_docker_compose(
                            mode, environment, api_url, key, secret
                        )
                        st.session_state.logs.append(
                            f"\n=== Docker Compose Start ===\n{output}\n"
                        )
                        time.sleep(2)
                        st.rerun()
                    except Exception as e:
                        st.error(f"Failed: {e}")
                        st.session_state.logs.append(f"\n=== Error ===\n{str(e)}\n")


# Main content - Logs
st.title("📋 Terminal / Container Logs")

if st.button("🔄 Refresh"):
    st.rerun()

# Build full log output
full_logs = []

# Add docker compose logs from session
if st.session_state.logs:
    full_logs.extend(st.session_state.logs)

# Add container logs if running
if st.session_state.is_running:
    container_logs = get_all_logs(container_name)
    if container_logs:
        full_logs.append(f"\n=== Container Logs ({container_name}) ===\n")
        full_logs.append(container_logs)

# Display logs
if full_logs:
    st.text_area(
        "Terminal Output",
        value="\n".join(full_logs),
        height=700,
        key="logs",
        label_visibility="collapsed",
    )

    if st.button("🗑️ Clear Logs"):
        st.session_state.logs = []
        st.rerun()
else:
    st.info("▶️ Start the trading algorithm to see logs here")

# Auto-refresh every 2 seconds when running
if st.session_state.is_running:
    time.sleep(2)
    st.rerun()
