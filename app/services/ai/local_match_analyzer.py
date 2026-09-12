import re


class LocalMatchAnalyzer:
    TECHNOLOGY_ALIASES = {
        "golang": "go",
        "nodejs": "node.js",
        "node": "node.js",
        "postgres": "postgresql",
        "postgres db": "postgresql",
        "js": "javascript",
        "ts": "typescript",
        "k8s": "kubernetes",
    }

    def analyze(self, resume_data: dict, job_data: dict) -> dict:
        required = self._build_required(job_data)
        technologies = self._build_technologies(job_data)
        preferred = self._build_preferred(job_data)
        candidate_text = self._candidate_text(resume_data)

        required = self._evaluate(required, candidate_text)
        technologies = self._evaluate(technologies, candidate_text)
        preferred = self._evaluate(preferred, candidate_text)
        all_requirements = required + technologies + preferred

        return {
            "required_requirements": required,
            "technology_requirements": technologies,
            "preferred_requirements": preferred,
            "strengths": [
                {
                    "strength": item["requirement"],
                    "importance": item["importance"],
                    "evidence_level": item["evidence_level"],
                    "evidence": item["evidence"],
                }
                for item in all_requirements
                if item["score"] >= 70
            ],
            "gaps": [
                {
                    "gap": item["requirement"],
                    "importance": item["importance"],
                    "recommendation": (
                        f"Consider gaining demonstrable experience with "
                        f"{item['requirement']}."
                    ),
                }
                for item in all_requirements
                if item["score"] < 40
            ],
            "overall_assessment": (
                "Match evaluated using local deterministic fallback analysis "
                "because the primary AI provider was unavailable."
            ),
        }

    def _candidate_text(self, resume_data: dict) -> str:
        parts = []
        for key in ("skills", "experience", "education"):
            value = resume_data.get(key) or []
            values = list(value.values()) if isinstance(value, dict) else value
            if not isinstance(values, (list, tuple)):
                values = [values]
            for item in values:
                if isinstance(item, dict):
                    parts.extend(str(v) for v in item.values() if v)
                else:
                    parts.append(str(item))
        parts.append(str(resume_data.get("summary") or ""))
        return " ".join(parts).lower()

    def _build_required(self, job_data):
        items = []
        for item in (job_data.get("required_skills") or []) + (job_data.get("responsibilities") or []):
            text = self._text(item)
            if text:
                items.append(self._base(item, text, "responsibility" if item in (job_data.get("responsibilities") or []) else "technical"))
        return items

    def _build_technologies(self, job_data):
        items = []
        for item in job_data.get("technologies") or []:
            text = self._text(item)
            if text:
                items.append(self._base(item, text, "technology"))
        return items

    def _build_preferred(self, job_data):
        items = []
        for item in (job_data.get("preferred_skills") or []) + (job_data.get("supporting_competencies") or []):
            text = self._text(item)
            if text:
                items.append(self._base(item, text, "competency"))
        return items

    @staticmethod
    def _text(item):
        return item.get("requirement") if isinstance(item, dict) else item if isinstance(item, str) else None

    @staticmethod
    def _base(item, text, category):
        return {
            "requirement": text,
            "category": item.get("category", category) if isinstance(item, dict) else category,
            "importance": item.get("importance", "medium") if isinstance(item, dict) else "medium",
        }

    def _evaluate(self, requirements, candidate_text):
        results = []
        for item in requirements:
            score, level, evidence, reason = self._match(item["requirement"], candidate_text)
            results.append({**item, "score": score, "evidence_level": level, "evidence": evidence, "reason": reason})
        return results

    def _match(self, requirement, candidate_text):
        normalized = self._normalize(requirement)
        if self._contains(normalized, candidate_text):
            return 100, "direct", [f"Candidate profile explicitly contains {requirement}."], f"Direct evidence of {requirement} in the candidate profile."

        words = [w for w in normalized.split() if len(w) > 2 and w not in {"and", "the", "with", "using", "experience", "knowledge", "ability"}]
        matched = [w for w in words if self._contains(w, candidate_text)]
        ratio = len(matched) / len(words) if words else 0
        if ratio >= 0.8:
            return 85, "direct", [f"Candidate profile contains related evidence: {', '.join(matched)}."], f"Strong evidence supporting {requirement}; most requirement concepts are present."
        if ratio >= 0.5:
            return 55, "indirect", [f"Candidate profile contains related concepts: {', '.join(matched)}."], f"Partial evidence for {requirement}; related experience is present but direct evidence is incomplete."
        return 0, "none", [], f"No meaningful evidence of {requirement} was found in the candidate profile."

    def _contains(self, value, text):
        value = self.TECHNOLOGY_ALIASES.get(value, value)
        if re.fullmatch(r"[a-z0-9.+#-]+", value):
            return bool(re.search(rf"(?<![a-z0-9]){re.escape(value)}(?![a-z0-9])", text))
        return value in text

    def _normalize(self, text):
        text = str(text).lower().strip()
        text = self.TECHNOLOGY_ALIASES.get(text, text)
        return re.sub(r"\s+", " ", re.sub(r"[^a-z0-9+#.\- ]+", " ", text))

