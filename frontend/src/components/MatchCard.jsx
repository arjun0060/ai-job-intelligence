import { useNavigate } from "react-router-dom";


function getMatchLabel(score) {
  if (score >= 80) {
    return {
      label: "Excellent Match",
      className: "bg-emerald-50 text-emerald-700",
    };
  }

  if (score >= 65) {
    return {
      label: "Strong Match",
      className: "bg-blue-50 text-blue-700",
    };
  }

  if (score >= 50) {
    return {
      label: "Moderate Match",
      className: "bg-amber-50 text-amber-700",
    };
  }

  return {
    label: "Low Match",
    className: "bg-red-50 text-red-700",
  };
}


function MatchCard({ match, rank }) {
  const navigate = useNavigate();

  const analysis = match.analysis_data || {};
  const job = match.job || {};

  const score = Number(
    analysis.overall_score ??
    match.overall_match_score ??
    0
  );

  const matchLabel = getMatchLabel(score);

  return (
    <div
      className="rounded-xl border border-slate-200 bg-white p-6 shadow-sm transition hover:-translate-y-0.5 hover:border-indigo-200 hover:shadow-md"
    >

      {/* Top section */}
      <div className="flex flex-col gap-5 md:flex-row md:items-start md:justify-between">

        {/* Job details */}
        <div className="flex min-w-0 gap-4">

          {/* Rank */}
          <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-lg bg-slate-100 text-sm font-bold text-slate-500">
            #{rank}
          </div>

          <div className="min-w-0">

            <div className="flex flex-wrap items-center gap-2">

              <h3 className="text-xl font-semibold text-slate-900">
                {job.title || `Job #${match.job_id}`}
              </h3>

              <span
                className={`rounded-full px-2.5 py-1 text-xs font-medium ${matchLabel.className}`}
              >
                {matchLabel.label}
              </span>

            </div>

            <p className="mt-2 text-sm font-medium text-slate-700">
              {job.company || "Company not specified"}
            </p>

            <div className="mt-2 flex flex-wrap gap-x-4 gap-y-1 text-sm text-slate-500">

              {job.location && (
                <span>
                  📍 {job.location}
                </span>
              )}

              {job.employment_type && (
                <span>
                  💼 {job.employment_type}
                </span>
              )}

              {job.department && (
                <span>
                  {job.department}
                </span>
              )}

            </div>

          </div>

        </div>


        {/* Score */}
        <div className="shrink-0 text-left md:text-right">

          <p className="text-xs font-medium uppercase tracking-wide text-slate-400">
            Match Score
          </p>

          <p className="mt-1 text-3xl font-bold text-indigo-600">
            {score.toFixed(2)}%
          </p>

        </div>

      </div>


      {/* Category scores */}
      <div className="mt-6 grid grid-cols-3 gap-3">

        <div className="rounded-lg bg-slate-50 p-3">

          <p className="text-xs text-slate-400">
            Required
          </p>

          <p className="mt-1 font-semibold text-slate-700">
            {Number(
              analysis.required_score ?? 0
            ).toFixed(2)}%
          </p>

        </div>


        <div className="rounded-lg bg-slate-50 p-3">

          <p className="text-xs text-slate-400">
            Technology
          </p>

          <p className="mt-1 font-semibold text-slate-700">
            {Number(
              analysis.technology_score ?? 0
            ).toFixed(2)}%
          </p>

        </div>


        <div className="rounded-lg bg-slate-50 p-3">

          <p className="text-xs text-slate-400">
            Preferred
          </p>

          <p className="mt-1 font-semibold text-slate-700">
            {Number(
              analysis.preferred_score ?? 0
            ).toFixed(2)}%
          </p>

        </div>

      </div>


      {/* Bottom actions */}
      <div className="mt-6 flex flex-col gap-3 border-t border-slate-100 pt-4 sm:flex-row sm:items-center sm:justify-between">

        <p className="text-xs text-slate-400">
          Match analysis #{match.id}
        </p>

        <div className="flex gap-4">

          {job.url && (
            <a
              href={job.url}
              target="_blank"
              rel="noopener noreferrer"
              onClick={(event) => {
                event.stopPropagation();
              }}
              className="text-sm font-medium text-slate-500 hover:text-slate-700"
            >
              View Job →
            </a>
          )}

          <button
            type="button"
            onClick={() => {
              navigate(`/matches/${match.id}`);
            }}
            className="text-sm font-semibold text-indigo-600 hover:text-indigo-700"
          >
            View Analysis →
          </button>

        </div>

      </div>

    </div>
  );
}


export default MatchCard;