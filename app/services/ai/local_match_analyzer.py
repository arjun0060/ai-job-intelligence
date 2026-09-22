import re
from datetime import datetime


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
        candidate_years = self._candidate_experience_years(
            resume_data.get("experience") or []
        )

        required = self._evaluate(
            required,
            candidate_text,
            candidate_years,
        )
        technologies = self._evaluate(
            technologies,
            candidate_text,
            candidate_years,
        )
        preferred = self._evaluate(
            preferred,
            candidate_text,
            candidate_years,
        )
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
        responsibilities = job_data.get("responsibilities") or []

        for item in (job_data.get("required_skills") or []) + responsibilities:
            text = self._text(item)
            if text:
                category = (
                    "responsibility"
                    if item in responsibilities
                    else "technical"
                )
                items.append(self._base(item, text, category))

        for item in job_data.get("education_requirements") or []:
            text = self._text(item)
            if text:
                items.append(self._base(item, text, "education"))

        experience = job_data.get("experience_requirement") or {}
        experience_text = self._experience_text(experience)
        if experience_text:
            items.append(
                {
                    "requirement": experience_text,
                    "category": "experience",
                    "importance": "high",
                }
            )

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
        for item in (
            job_data.get("preferred_skills") or []
        ) + (
            job_data.get("supporting_competencies") or []
        ):
            text = self._text(item)
            if text:
                items.append(self._base(item, text, "competency"))
        return items

    @staticmethod
    def _text(item):
        if isinstance(item, dict):
            return item.get("requirement")
        if isinstance(item, str):
            return item
        return None

    @staticmethod
    def _base(item, text, category):
        return {
            "requirement": text,
            "category": (
                item.get("category", category)
                if isinstance(item, dict)
                else category
            ),
            "importance": (
                item.get("importance", "medium")
                if isinstance(item, dict)
                else "medium"
            ),
        }

    def _evaluate(self, requirements, candidate_text, candidate_years):
        results = []
        for item in requirements:
            if item["category"] == "experience":
                score, level, evidence, reason = self._match_experience(
                    item["requirement"],
                    candidate_years,
                )
            else:
                score, level, evidence, reason = self._match(
                    item["requirement"],
                    candidate_text,
                )

            results.append(
                {
                    **item,
                    "score": score,
                    "evidence_level": level,
                    "evidence": evidence,
                    "reason": reason,
                }
            )
        return results

    def _match_experience(self, requirement, candidate_years):
        required_min, required_max = self._extract_required_years(
            requirement
        )

        if required_min is None and required_max is None:
            return self._match(requirement, "")

        if candidate_years is None:
            return (
                0,
                "none",
                [],
                "The resume does not provide enough explicit duration "
                "information to verify the experience requirement.",
            )

        if required_min is not None and candidate_years >= required_min:
            return (
                100,
                "direct",
                [
                    f"Candidate experience is approximately "
                    f"{candidate_years:.1f} years."
                ],
                "The documented experience meets the minimum duration "
                "requirement.",
            )

        if required_min is not None:
            ratio = candidate_years / required_min if required_min else 0
            score = round(max(0, min(85, ratio * 85)), 2)
            return (
                score,
                "indirect" if candidate_years > 0 else "none",
                [
                    f"Candidate experience is approximately "
                    f"{candidate_years:.1f} years, below the required "
                    f"{required_min:g} years."
                ],
                "The candidate has relevant documented experience but "
                "does not meet the stated minimum duration.",
            )

        if required_max is not None and candidate_years <= required_max:
            return (
                100,
                "direct",
                [f"Candidate experience is approximately {candidate_years:.1f} years."],
                "The documented experience is within the stated range.",
            )

        return (
            0,
            "indirect",
            [f"Candidate experience is approximately {candidate_years:.1f} years."],
            "The documented experience exceeds the stated maximum.",
        )

    def _match(self, requirement, candidate_text):
        normalized = self._normalize(requirement)
        if self._contains(normalized, candidate_text):
            return (
                100,
                "direct",
                [
                    f"Candidate profile explicitly contains {requirement}."
                ],
                f"Direct evidence of {requirement} in the candidate profile.",
            )

        words = [
            w
            for w in normalized.split()
            if len(w) > 2
            and w not in {
                "and",
                "the",
                "with",
                "using",
                "experience",
                "knowledge",
                "ability",
                "professional",
            }
        ]
        matched = [w for w in words if self._contains(w, candidate_text)]
        ratio = len(matched) / len(words) if words else 0

        if ratio >= 0.8:
            return (
                85,
                "direct",
                [
                    "Candidate profile contains related evidence: "
                    f"{', '.join(matched)}."
                ],
                f"Strong evidence supporting {requirement}; most requirement "
                "concepts are present.",
            )

        if ratio >= 0.5:
            return (
                55,
                "indirect",
                [
                    "Candidate profile contains related concepts: "
                    f"{', '.join(matched)}."
                ],
                f"Partial evidence for {requirement}; related experience is "
                "present but direct evidence is incomplete.",
            )

        return (
            0,
            "none",
            [],
            f"No meaningful evidence of {requirement} was found in the "
            "candidate profile.",
        )

    @staticmethod
    def _experience_text(experience_requirement):
        minimum = experience_requirement.get("minimum_years")
        maximum = experience_requirement.get("maximum_years")
        description = experience_requirement.get("description")

        if minimum is not None and maximum is not None:
            return (
                f"At least {float(minimum):g} years of experience and no more "
                f"than {float(maximum):g} years"
            )
        if minimum is not None:
            return f"At least {float(minimum):g} years of professional experience"
        if maximum is not None:
            return f"No more than {float(maximum):g} years of professional experience"
        return str(description).strip() if description else None

    @staticmethod
    def _extract_required_years(requirement):
        range_match = re.search(
            r"at least\s+(\d+(?:\.\d+)?)\s+years?.*?no more than\s+(\d+(?:\.\d+)?)",
            requirement.lower(),
        )
        if range_match:
            return float(range_match.group(1)), float(range_match.group(2))

        minimum_match = re.search(
            r"at least\s+(\d+(?:\.\d+)?)\s+years?",
            requirement.lower(),
        )
        if minimum_match:
            return float(minimum_match.group(1)), None

        maximum_match = re.search(
            r"no more than\s+(\d+(?:\.\d+)?)\s+years?",
            requirement.lower(),
        )
        if maximum_match:
            return None, float(maximum_match.group(1))

        return None, None

    @staticmethod
    def _candidate_experience_years(experience):
        if not experience:
            return None

        if isinstance(experience, dict):
            experience = [experience]
        if not isinstance(experience, (list, tuple)):
            return None

        total_months = 0
        found_duration = False

        for item in experience:
            if not isinstance(item, dict):
                continue

            duration = str(item.get("duration") or "")
            duration_match = re.search(
                r"(?:(\d+(?:\.\d+)?)\s*(?:years?|yrs?))?"
                r"\s*(?:(\d+)\s*(?:months?|mos?))?",
                duration.lower(),
            )
            if duration_match and (
                duration_match.group(1) or duration_match.group(2)
            ):
                years = float(duration_match.group(1) or 0)
                months = int(duration_match.group(2) or 0)
                total_months += round(years * 12) + months
                found_duration = True
                continue

            start, end = LocalMatchAnalyzer._extract_dates(item)
            if start:
                end = end or datetime.now()
                if end >= start:
                    total_months += (
                        (end.year - start.year) * 12
                        + end.month
                        - start.month
                        + 1
                    )
                    found_duration = True

        if not found_duration:
            return None

        return round(total_months / 12, 2)

    @staticmethod
    def _extract_dates(item):
        text = " ".join(
            str(item.get(key) or "")
            for key in ("start_date", "end_date", "from", "to", "duration")
        )
        matches = re.findall(
            r"(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+(\d{4})",
            text,
            re.IGNORECASE,
        )
        if not matches:
            return None, None

        parsed = []
        for month, year in matches:
            try:
                parsed.append(
                    datetime.strptime(
                        f"{month} {year}",
                        "%b %Y",
                    )
                )
            except ValueError:
                continue

        if not parsed:
            return None, None

        if len(parsed) == 1:
            return parsed[0], None
        return parsed[0], parsed[1]

    def _contains(self, value, text):
        value = self.TECHNOLOGY_ALIASES.get(value, value)
        if re.fullmatch(r"[a-z0-9.+#-]+", value):
            return bool(
                re.search(
                    rf"(?<![a-z0-9]){re.escape(value)}(?![a-z0-9])",
                    text,
                )
            )
        return value in text

    def _normalize(self, text):
        text = str(text).lower().strip()
        text = self.TECHNOLOGY_ALIASES.get(text, text)
        return re.sub(
            r"\s+",
            " ",
            re.sub(r"[^a-z0-9+#.\- ]+", " ", text),
        )
