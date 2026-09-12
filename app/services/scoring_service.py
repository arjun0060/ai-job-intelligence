class ScoringService:

    REQUIRED_WEIGHT = 0.50
    TECHNOLOGY_WEIGHT = 0.35
    PREFERRED_WEIGHT = 0.15

    IMPORTANCE_WEIGHTS = {
        "critical": 1.5,
        "high": 1.2,
        "medium": 1.0,
        "low": 0.7,
    }

    @classmethod
    def calculate_final_score(
        cls,
        required_requirements: list,
        preferred_requirements: list,
        technology_requirements: list,
    ) -> dict:

        # Calculate category scores
        required_score = (
            cls._calculate_weighted_average_score(
                required_requirements
            )
        )

        technology_score = (
            cls._calculate_weighted_average_score(
                technology_requirements
            )
        )

        preferred_score = (
            cls._calculate_weighted_average_score(
                preferred_requirements
            )
        )

        # ---------------------------------------------------------
        # Category weights
        # ---------------------------------------------------------

        categories = []

        if required_requirements:
            categories.append(
                (
                    "required",
                    required_score,
                    cls.REQUIRED_WEIGHT,
                )
            )

        if technology_requirements:
            categories.append(
                (
                    "technology",
                    technology_score,
                    cls.TECHNOLOGY_WEIGHT,
                )
            )

        if preferred_requirements:
            categories.append(
                (
                    "preferred",
                    preferred_score,
                    cls.PREFERRED_WEIGHT,
                )
            )

        total_weight = sum(
            weight
            for _, _, weight in categories
        )

        # ---------------------------------------------------------
        # Score breakdown
        # ---------------------------------------------------------

        score_breakdown = {}

        overall_score = 0

        for name, score, configured_weight in categories:

            effective_weight = (
                configured_weight / total_weight
                if total_weight
                else 0
            )

            contribution = (
                score * effective_weight
            )

            score_breakdown[name] = {
                "score": round(score, 2),
                "configured_weight": round(
                    configured_weight,
                    2,
                ),
                "effective_weight": round(
                    effective_weight,
                    4,
                ),
                "contribution": round(
                    contribution,
                    2,
                ),
            }

            overall_score += contribution

        # ---------------------------------------------------------
        # Critical requirement penalty
        # ---------------------------------------------------------

        critical_penalty = (
            cls._calculate_critical_penalty(
                required_requirements
            )
        )

        final_score = max(
            0,
            overall_score - critical_penalty,
        )

        score_breakdown["critical_penalty"] = round(
            critical_penalty,
            2,
        )

        score_breakdown["final_score"] = round(
            final_score,
            2,
        )

        return {
            "required_score": round(
                required_score,
                2,
            ),
            "technology_score": round(
                technology_score,
                2,
            ),
            "preferred_score": round(
                preferred_score,
                2,
            ),
            "critical_penalty": round(
                critical_penalty,
                2,
            ),
            "overall_score": round(
                final_score,
                2,
            ),
            "score_breakdown": score_breakdown,
        }

    @classmethod
    def _calculate_weighted_average_score(
        cls,
        requirements: list,
    ) -> float:

        if not requirements:
            return 0

        weighted_score_sum = 0
        total_weight = 0

        for requirement in requirements:

            score = requirement.get(
                "score",
                0,
            )

            importance = requirement.get(
                "importance",
                "medium",
            ).lower()

            weight = cls.IMPORTANCE_WEIGHTS.get(
                importance,
                cls.IMPORTANCE_WEIGHTS["medium"],
            )

            weighted_score_sum += (
                score * weight
            )

            total_weight += weight

        if total_weight == 0:
            return 0

        return (
            weighted_score_sum
            / total_weight
        )

    @staticmethod
    def _calculate_critical_penalty(
        required_requirements: list,
    ) -> float:

        critical_missing = 0

        for requirement in required_requirements:

            importance = requirement.get(
                "importance",
                "medium",
            ).lower()

            score = requirement.get(
                "score",
                0,
            )

            if (
                importance == "critical"
                and score < 40
            ):
                critical_missing += 1

        return min(
            critical_missing * 10,
            20,
        )