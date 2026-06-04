import logging
import time
from typing import Optional
from sqlalchemy.orm import Session

from app.db.models import AgentRun, LLMCall
from app.db.session import SessionLocal

logger = logging.getLogger(__name__)


class AgentLogger:
    """Logs agent runs and LLM calls to the database."""

    def __init__(self, agent_name: str):
        self.agent_name = agent_name
        self._run_id: Optional[int] = None
        self._start_time: Optional[float] = None
        self._success = True
        self._error_msg = ""

    def start(self):
        self._start_time = time.time()

    def end(self, success: bool = True, error_msg: str = ""):
        self._success = success
        self._error_msg = error_msg
        self._flush()

    def log_llm_call(
        self,
        model: str,
        prompt_tokens: Optional[int] = None,
        completion_tokens: Optional[int] = None,
        temperature: Optional[float] = None,
        duration_ms: Optional[int] = None,
    ):
        db = SessionLocal()
        try:
            if self._run_id is None:
                run = AgentRun(
                    agent_name=self.agent_name,
                    success=self._success,
                    error_msg=self._error_msg,
                    duration_ms=int((time.time() - self._start_time) * 1000) if self._start_time else None,
                )
                db.add(run)
                db.flush()
                self._run_id = run.id

            call = LLMCall(
                agent_run_id=self._run_id,
                model=model,
                prompt_tokens=prompt_tokens,
                completion_tokens=completion_tokens,
                temperature=temperature,
                duration_ms=duration_ms,
            )
            db.add(call)
            db.commit()
        except Exception as e:
            db.rollback()
            logger.warning(f"Failed to log LLM call: {e}")
        finally:
            db.close()

    def _flush(self):
        db = SessionLocal()
        try:
            if self._run_id is not None:
                run = db.get(AgentRun, self._run_id)
                if run:
                    run.success = self._success
                    run.error_msg = self._error_msg
                    if self._start_time:
                        run.duration_ms = int((time.time() - self._start_time) * 1000)
                    db.commit()
        except Exception as e:
            db.rollback()
            logger.warning(f"Failed to flush agent log: {e}")
        finally:
            db.close()
