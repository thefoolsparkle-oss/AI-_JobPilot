import os
import json
import pytest

os.environ["DATABASE_URL"] = "sqlite:///./test_jobpilot.db"
os.environ["JOBPILOT_SETTINGS_FILE"] = os.path.join(os.path.dirname(__file__), "..", "test_settings.json")
os.environ["JOBPILOT_SECRET_KEY_FILE"] = os.path.join(os.path.dirname(__file__), "..", "test_secret_key")
os.environ["RATE_LIMIT_ENABLED"] = "false"

from app.db.session import engine, Base


@pytest.fixture(scope="session", autouse=True)
def setup_db():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


class TestLLMFactory:
    def test_get_llm_returns_same_instance(self):
        from app.llm.factory import get_llm, reset_llm
        reset_llm()
        llm1 = get_llm()
        llm2 = get_llm()
        assert llm1 is llm2

    def test_reset_creates_new_instance(self):
        from app.llm.factory import get_llm, reset_llm
        reset_llm()
        llm1 = get_llm()
        reset_llm()
        llm2 = get_llm()
        assert llm1 is not llm2

    def test_get_llm_returns_deepseek_provider(self):
        from app.llm.factory import get_llm, reset_llm
        from app.llm.deepseek_provider import DeepSeekProvider
        reset_llm()
        llm = get_llm()
        assert isinstance(llm, DeepSeekProvider)


class TestDeepSeekProvider:
    def test_provider_has_required_attributes(self):
        from app.llm.deepseek_provider import DeepSeekProvider
        provider = DeepSeekProvider()
        assert hasattr(provider, "fast_model")
        assert hasattr(provider, "reasoning_model")
        assert hasattr(provider, "client")

    def test_provider_models_from_config(self):
        from app.llm.deepseek_provider import DeepSeekProvider
        provider = DeepSeekProvider()
        assert provider.fast_model == "deepseek-chat"
        assert provider.reasoning_model == "deepseek-reasoner"

    def test_build_kwargs_basic(self):
        from app.llm.deepseek_provider import DeepSeekProvider
        provider = DeepSeekProvider()
        kwargs = provider._build_kwargs(
            model="deepseek-chat",
            messages=[{"role": "user", "content": "hi"}],
            response_format=None,
            temperature=None,
            max_tokens=None,
        )
        assert kwargs["model"] == "deepseek-chat"
        assert kwargs["messages"] == [{"role": "user", "content": "hi"}]
        assert kwargs["temperature"] == provider.default_temperature

    def test_build_kwargs_with_all_options(self):
        from app.llm.deepseek_provider import DeepSeekProvider
        provider = DeepSeekProvider()
        kwargs = provider._build_kwargs(
            model="deepseek-chat",
            messages=[],
            response_format={"type": "json_object"},
            temperature=0.5,
            max_tokens=1000,
        )
        assert kwargs["response_format"] == {"type": "json_object"}
        assert kwargs["temperature"] == 0.5
        assert kwargs["max_tokens"] == 1000

    def test_achat_client_lazy_initialized(self):
        from app.llm.deepseek_provider import DeepSeekProvider
        provider = DeepSeekProvider()
        assert provider._aclient is None
        client = provider._get_aclient()
        assert client is not None
        assert provider._aclient is not None


class TestOpenAIProvider:
    def test_init_stores_params(self):
        from app.llm.openai_provider import OpenAIProvider
        provider = OpenAIProvider(api_key="sk-test", base_url="https://api.test.com/v1", model="gpt-4")
        assert provider.default_model == "gpt-4"
        assert provider.default_temperature == 0.2

    def test_build_kwargs(self):
        from app.llm.openai_provider import OpenAIProvider
        provider = OpenAIProvider(api_key="sk-test", base_url="https://api.test.com/v1", model="gpt-4")
        kwargs = provider._build_kwargs(
            model="gpt-4", messages=[], response_format=None, temperature=None, max_tokens=None,
        )
        assert kwargs["model"] == "gpt-4"
        assert kwargs["temperature"] == 0.2

    def test_achat_client_lazy(self):
        from app.llm.openai_provider import OpenAIProvider
        provider = OpenAIProvider(api_key="sk-test", base_url="https://api.test.com/v1", model="gpt-4")
        assert provider._aclient is None
        client = provider._get_aclient()
        assert client is not None
        assert provider._aclient is not None


class TestSettingsStore:
    SETTINGS = os.path.join(os.path.dirname(__file__), "..", "test_settings.json")
    SECRET = os.path.join(os.path.dirname(__file__), "..", "test_secret_key")

    def setup_method(self):
        for f in [self.SETTINGS, self.SECRET]:
            if os.path.exists(f):
                os.remove(f)

    def test_get_key_empty(self):
        from app.services.settings_service import SettingsStore
        store = SettingsStore()
        assert store.get_key() == ""

    def test_has_key_false_initially(self):
        from app.services.settings_service import SettingsStore
        store = SettingsStore()
        assert store.has_key() is False

    def test_set_and_get_key(self):
        from app.services.settings_service import SettingsStore
        store = SettingsStore()
        store.set_key("sk-test-12345")
        assert store.get_key() == "sk-test-12345"
        assert store.has_key() is True

    def test_masked_key_format(self):
        from app.services.settings_service import SettingsStore
        store = SettingsStore()
        store.set_key("sk-abcdefghijklmnop")
        masked = store.get_masked_key()
        assert masked.startswith("sk-")
        assert len(masked) > 8
        assert "*" in masked

    def test_masked_short_key(self):
        from app.services.settings_service import SettingsStore
        store = SettingsStore()
        store.set_key("sk-ab")
        masked = store.get_masked_key()
        assert "sk-ab" in masked or "*" in masked

    def test_get_models_defaults(self):
        from app.services.settings_service import SettingsStore
        store = SettingsStore()
        models = store.get_models()
        assert models["fast_model"] == "deepseek-chat"
        assert models["reasoning_model"] == "deepseek-reasoner"
        assert "https://api.deepseek.com" in models["base_url"]

    def test_set_model_config(self):
        from app.services.settings_service import SettingsStore
        store = SettingsStore()
        store.set_model_config(base_url="https://custom.api/v1", fast_model="custom-fast", reasoning_model="custom-reason")
        models = store.get_models()
        assert models["base_url"] == "https://custom.api/v1"
        assert models["fast_model"] == "custom-fast"
        assert models["reasoning_model"] == "custom-reason"

    def test_set_model_partial(self):
        from app.services.settings_service import SettingsStore
        store = SettingsStore()
        store.set_model_config(fast_model="new-fast")
        models = store.get_models()
        assert models["fast_model"] == "new-fast"
        assert models["reasoning_model"] == "deepseek-reasoner"


class TestAgentLogger:
    def test_agent_logger_init(self):
        from app.services.agent_logger import AgentLogger
        alog = AgentLogger("test_agent")
        assert alog.agent_name == "test_agent"
        assert alog._run_id is None

    def test_start_logs_timing(self):
        import time
        from app.services.agent_logger import AgentLogger
        alog = AgentLogger("timing_agent")
        alog.start()
        assert alog._start_time is not None
        assert alog._start_time > 0

    def test_log_llm_call_creates_run(self):
        from app.services.agent_logger import AgentLogger
        alog = AgentLogger("run_test_agent")
        alog.start()
        alog.log_llm_call(model="deepseek-chat", prompt_tokens=100, completion_tokens=50, temperature=0.2, duration_ms=500)
        assert alog._run_id is not None

    def test_end_flushes(self):
        from app.services.agent_logger import AgentLogger
        alog = AgentLogger("end_test_agent")
        alog.start()
        alog.end(success=True, error_msg="")
