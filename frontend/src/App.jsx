import { useEffect, useState } from "react";
import { useParams } from "react-router-dom";

import { getMatch } from "./services/api";

import ScoreCard from "./components/ScoreCard";
import ScoreBreakdown from "./components/ScoreBreakdown";
import RequirementTable from "./components/RequirementTable";


function App() {
  const { matchId } = useParams();

  const [match, setMatch] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);


  useEffect(() => {
    const loadMatch = async () => {
      try {
        setLoading(true);
        setError(null);

        const data = await getMatch(matchId);

        setMatch(data);
      } catch (err) {
        console.error(err);

        setError(
          err.response?.data?.detail ||
          "Failed to load match analysis."
        );
      } finally {
        setLoading(false);
      }
    };


    if (matchId) {
      loadMatch();
    }
  }, [matchId]);


  if (loading) {
    return (
      <div className="flex min-h-screen items-center justify-center bg-slate-50">
        <div className="text-sm text-slate-500">
          Loading match analysis...
        </div>
      </div>
    );
  }


  if (error) {
    return (
      <div className="flex min-h-screen items-center justify-center bg-slate-50">
        <div className="rounded-xl border border-red-200 bg-white p-6 text-center shadow-sm">
          <h2 className="font-semibold text-red-600">
            Unable to load analysis
          </h2>

          <p className="mt-2 text-sm text-slate-500">
            {error}
          </p>
        </div>
      </div>
    );
  }


  if (!match) {
    return (
      <div className="flex min-h-screen items-center justify-center bg-slate-50">
        <div className="rounded-xl border border-slate-200 bg-white p-6 text-center shadow-sm">
          <h2 className="font-semibold text-slate-900">
            Match analysis not found
          </h2>

          <p className="mt-2 text-sm text-slate-500">
            The requested match analysis could not be found.
          </p>
        </div>
      </div>
    );
  }


  /*
   * Normalize old and new match-analysis response shapes.
   *
   * Older records may store values directly under analysis_data.
   * Newer records may also expose the final/category scores through
   * score_breakdown or overall_match_score.
   *
   * Keeping this normalization in the frontend allows both formats
   * to render without changing the backend or existing database rows.
   */
  const rawAnalysis = match.analysis_data || {};
  const scoreBreakdown = rawAnalysis.score_breakdown || {};

  const requiredBreakdown =
    scoreBreakdown.required || {};

  const technologyBreakdown =
    scoreBreakdown.technology || {};

  const preferredBreakdown =
    scoreBreakdown.preferred || {};

  const analysis = {
    ...rawAnalysis,

    overall_score: Number(
      rawAnalysis.overall_score ??
      match.overall_match_score ??
      scoreBreakdown.final_score ??
      0
    ),

    required_score: Number(
      rawAnalysis.required_score ??
      requiredBreakdown.score ??
      0
    ),

    technology_score: Number(
      rawAnalysis.technology_score ??
      technologyBreakdown.score ??
      0
    ),

    preferred_score: Number(
      rawAnalysis.preferred_score ??
      preferredBreakdown.score ??
      0
    ),

    score_breakdown: scoreBreakdown,

    overall_assessment:
      rawAnalysis.overall_assessment ||
      rawAnalysis.summary ||
      "No overall assessment was provided for this match.",

    strengths: Array.isArray(rawAnalysis.strengths)
      ? rawAnalysis.strengths
      : [],

    gaps: Array.isArray(rawAnalysis.gaps)
      ? rawAnalysis.gaps
      : [],

    required_requirements: Array.isArray(
      rawAnalysis.required_requirements
    )
      ? rawAnalysis.required_requirements
      : [],

    technology_requirements: Array.isArray(
      rawAnalysis.technology_requirements
    )
      ? rawAnalysis.technology_requirements
      : [],

    preferred_requirements: Array.isArray(
      rawAnalysis.preferred_requirements
    )
      ? rawAnalysis.preferred_requirements
      : [],
  };


  const analysisProvider = analysis.analysis_provider;
  const isLocalFallback = analysisProvider === "local";


  return (
    <div className="min-h-screen bg-slate-50">

      {/* Header */}
      <header className="border-b border-slate-200 bg-white">
        <div className="mx-auto max-w-7xl px-6 py-5">

          <h1 className="text-2xl font-bold text-slate-900">
            AI Job Intelligence
          </h1>

          <p className="mt-1 text-sm text-slate-500">
            Resume and job compatibility analysis
          </p>

        </div>
      </header>


      <main className="mx-auto max-w-7xl px-6 py-8">

        {/* Match Header */}
        <section className="mb-8">

          <div className="flex flex-col justify-between gap-4 md:flex-row md:items-center">

            <div>

              <p className="text-sm font-medium text-indigo-600">
                Match Analysis #{match.id}
              </p>

              <h2 className="mt-1 text-3xl font-bold text-slate-900">
                Resume vs Job
              </h2>

              <div className="mt-2 space-y-1 text-sm text-slate-500">

                <p>
                  Resume ID: {match.resume_id}
                </p>

                <p>
                  Job ID: {match.job_id}
                </p>

              </div>

            </div>


            {/* Overall Score */}
            <div className="rounded-2xl border border-slate-200 bg-white px-8 py-5 text-center shadow-sm">

              <p className="text-sm font-medium text-slate-500">
                Overall Match
              </p>

              <p className="mt-1 text-4xl font-bold text-indigo-600">
                {analysis.overall_score.toFixed(2)}%
              </p>

              <div className="mt-3 flex justify-center">

                <span
                  className={`rounded-full px-3 py-1 text-xs font-medium ${
                    isLocalFallback
                      ? "bg-amber-50 text-amber-700"
                      : "bg-emerald-50 text-emerald-700"
                  }`}
                >
                  Analysis method:{" "}
                  {isLocalFallback
                    ? "Local fallback"
                    : "Gemini AI"}
                </span>

              </div>

            </div>

          </div>

        </section>


        {/* Fallback Notice */}
        {isLocalFallback && (
          <section className="mb-8 rounded-xl border border-amber-200 bg-amber-50 p-5">

            <div className="flex gap-3">

              <span className="mt-0.5 text-amber-600">
                ⓘ
              </span>

              <div>

                <h2 className="font-semibold text-amber-900">
                  Local analysis was used
                </h2>

                <p className="mt-1 text-sm leading-6 text-amber-800">
                  The primary AI provider was unavailable, so this
                  match was evaluated using the local deterministic
                  analyzer.
                </p>

              </div>

            </div>

          </section>
        )}


        {/* Score Cards */}
        <section className="mb-8 grid gap-5 md:grid-cols-3">

          <ScoreCard
            title="Required Requirements"
            score={analysis.required_score}
            description="Core requirements"
          />

          <ScoreCard
            title="Technology"
            score={analysis.technology_score}
            description="Technology and tools"
          />

          <ScoreCard
            title="Preferred Requirements"
            score={analysis.preferred_score}
            description="Additional qualifications"
          />

        </section>


        {/* Score Breakdown */}
        <section className="mb-8">

          <ScoreBreakdown
            breakdown={analysis.score_breakdown}
          />

        </section>


        {/* Overall Assessment */}
        <section className="mb-8 rounded-xl border border-slate-200 bg-white p-6 shadow-sm">

          <h2 className="text-lg font-semibold text-slate-900">
            Overall Assessment
          </h2>

          <p className="mt-3 leading-7 text-slate-600">
            {analysis.overall_assessment}
          </p>

        </section>


        {/* Strengths + Gaps */}
        <section className="grid gap-6 lg:grid-cols-2">

          {/* Strengths */}
          <div className="rounded-xl border border-slate-200 bg-white p-6 shadow-sm">

            <h2 className="text-lg font-semibold text-slate-900">
              Strengths
            </h2>

            <div className="mt-5 space-y-3">

              {analysis.strengths.length === 0 ? (

                <p className="text-sm text-slate-500">
                  No strengths were provided for this analysis.
                </p>

              ) : (

                analysis.strengths.map(
                  (strength, index) => (
                    <div
                      key={index}
                      className="flex gap-3"
                    >

                      <span className="mt-1 text-emerald-500">
                        ✓
                      </span>

                      <p className="text-sm leading-6 text-slate-600">
                        {typeof strength === "string"
                          ? strength
                          : strength?.description ||
                            strength?.text ||
                            JSON.stringify(strength)}
                      </p>

                    </div>
                  )
                )

              )}

            </div>

          </div>


          {/* Gaps */}
          <div className="rounded-xl border border-slate-200 bg-white p-6 shadow-sm">

            <h2 className="text-lg font-semibold text-slate-900">
              Skill Gaps
            </h2>

            <div className="mt-5 space-y-4">

              {analysis.gaps.length === 0 ? (

                <p className="text-sm text-slate-500">
                  No skill gaps were identified.
                </p>

              ) : (

                analysis.gaps.map(
                  (gap, index) => {

                    const gapText =
                      typeof gap === "string"
                        ? gap
                        : gap?.gap ||
                          gap?.description ||
                          gap?.text ||
                          "Unspecified gap";

                    const importance =
                      typeof gap === "object"
                        ? gap?.importance || "medium"
                        : "medium";

                    const recommendation =
                      typeof gap === "object"
                        ? gap?.recommendation ||
                          gap?.reason ||
                          ""
                        : "";

                    return (
                      <div
                        key={index}
                        className="border-b border-slate-100 pb-4 last:border-0 last:pb-0"
                      >

                        <div className="flex items-start justify-between gap-4">

                          <p className="text-sm font-medium text-slate-700">
                            {gapText}
                          </p>

                          <span className="shrink-0 rounded-full bg-amber-50 px-2.5 py-1 text-xs font-medium capitalize text-amber-700">
                            {importance}
                          </span>

                        </div>

                        {recommendation && (
                          <p className="mt-2 text-sm leading-6 text-slate-500">
                            {recommendation}
                          </p>
                        )}

                      </div>
                    );
                  }
                )

              )}

            </div>

          </div>

        </section>


        {/* Requirement Analysis */}
        <section className="mt-8 space-y-6">

          <RequirementTable
            title="Required Requirements"
            description="Core requirements evaluated against the candidate profile."
            requirements={
              analysis.required_requirements
            }
          />


          <RequirementTable
            title="Technology Requirements"
            description="Technologies, frameworks, databases, and infrastructure mentioned in the job."
            requirements={
              analysis.technology_requirements
            }
          />


          <RequirementTable
            title="Preferred Requirements"
            description="Additional qualifications that improve the candidate's fit."
            requirements={
              analysis.preferred_requirements
            }
          />

        </section>

      </main>

    </div>
  );
}


export default App;