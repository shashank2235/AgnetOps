from pathlib import Path

import yaml

from app.schemas.agent import GuardrailCheckOut


class GuardrailsService:
    def __init__(self, policy_path: str | None = None) -> None:
        if policy_path is None:
            policy_path = str(Path(__file__).with_name("policy.yaml"))
        with open(policy_path, "r", encoding="utf-8") as f:
            self.policy = yaml.safe_load(f)

    def check(self, text: str) -> GuardrailCheckOut:
        lower = text.lower()
        violations: list[str] = []
        action = "allow"

        pi = self.policy["policies"]["prompt_injection"]
        if any(k in lower for k in pi["keywords"]):
            violations.append("prompt_injection")
            action = "block"

        pii = self.policy["policies"]["pii"]
        if any(p in lower for p in pii["patterns"]):
            violations.append("pii_detected")
            if action == "allow":
                action = "warn"

        unsafe = self.policy["policies"]["unsafe_domains"]
        all_unsafe = unsafe["medical_keywords"] + unsafe["legal_keywords"] + unsafe["financial_keywords"]
        if any(k in lower for k in all_unsafe):
            violations.append("unsafe_domain_claim")
            if action in {"allow", "warn"}:
                action = "human_approval"

        return GuardrailCheckOut(action=action, violations=violations)
