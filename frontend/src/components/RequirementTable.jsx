function getScoreClass(score) {
  if (score >= 75) {
    return "text-emerald-600 bg-emerald-50";
  }

  if (score >= 50) {
    return "text-amber-600 bg-amber-50";
  }

  return "text-red-600 bg-red-50";
}

function getEvidenceClass(level) {
  switch (level) {
    case "direct":
      return "bg-emerald-50 text-emerald-700";

    case "indirect":
      return "bg-amber-50 text-amber-700";

    case "none":
      return "bg-red-50 text-red-700";

    default:
      return "bg-slate-100 text-slate-600";
  }
}

function RequirementTable({
  title,
  description,
  requirements = [],
}) {
  return (
    <section className="rounded-xl border border-slate-200 bg-white shadow-sm">

      {/* Header */}
      <div className="border-b border-slate-200 p-6">
        <h2 className="text-lg font-semibold text-slate-900">
          {title}
        </h2>

        {description && (
          <p className="mt-1 text-sm text-slate-500">
            {description}
          </p>
        )}
      </div>

      {/* Requirements */}
      <div className="divide-y divide-slate-100">

        {requirements.length === 0 ? (
          <div className="p-6 text-sm text-slate-500">
            No requirements available.
          </div>
        ) : (
          requirements.map((item, index) => (
            <div
              key={`${item.requirement}-${index}`}
              className="p-6"
            >

              {/* Requirement header */}
              <div className="flex flex-col gap-3 md:flex-row md:items-start md:justify-between">

                <div className="min-w-0">
                  <h3 className="font-medium text-slate-900">
                    {item.requirement}
                  </h3>

                  <div className="mt-2 flex flex-wrap gap-2">

                    {item.importance && (
                      <span className="rounded-full bg-slate-100 px-2.5 py-1 text-xs font-medium capitalize text-slate-600">
                        {item.importance}
                      </span>
                    )}

                    {item.evidence_level && (
                      <span
                        className={`rounded-full px-2.5 py-1 text-xs font-medium capitalize ${getEvidenceClass(
                          item.evidence_level
                        )}`}
                      >
                        {item.evidence_level} evidence
                      </span>
                    )}

                    {item.category && (
                      <span className="rounded-full bg-indigo-50 px-2.5 py-1 text-xs font-medium capitalize text-indigo-600">
                        {item.category}
                      </span>
                    )}

                  </div>
                </div>

                {/* Score */}
                <div
                  className={`w-fit shrink-0 rounded-lg px-3 py-2 text-center ${getScoreClass(
                    item.score
                  )}`}
                >
                  <div className="text-lg font-bold">
                    {Number(item.score).toFixed(0)}%
                  </div>

                  <div className="text-[10px] font-medium uppercase tracking-wide">
                    Match
                  </div>
                </div>

              </div>

              {/* Progress bar */}
              <div className="mt-5">
                <div className="h-2 overflow-hidden rounded-full bg-slate-100">
                  <div
                    className="h-full rounded-full bg-indigo-500 transition-all"
                    style={{
                      width: `${Math.min(
                        Math.max(Number(item.score) || 0, 0),
                        100
                      )}%`,
                    }}
                  />
                </div>
              </div>

              {/* Evidence */}
              <div className="mt-5">

                <h4 className="text-xs font-semibold uppercase tracking-wide text-slate-400">
                  Evidence
                </h4>

                {item.evidence?.length > 0 ? (
                  <ul className="mt-2 space-y-1">
                    {item.evidence.map(
                      (evidence, evidenceIndex) => (
                        <li
                          key={evidenceIndex}
                          className="flex gap-2 text-sm text-slate-600"
                        >
                          <span className="text-slate-400">
                            •
                          </span>

                          <span>
                            {evidence}
                          </span>
                        </li>
                      )
                    )}
                  </ul>
                ) : (
                  <p className="mt-2 text-sm italic text-slate-400">
                    No supporting evidence found.
                  </p>
                )}

              </div>

              {/* Reason */}
              {item.reason && (
                <div className="mt-5 rounded-lg bg-slate-50 p-4">

                  <h4 className="text-xs font-semibold uppercase tracking-wide text-slate-400">
                    Analysis
                  </h4>

                  <p className="mt-2 text-sm leading-6 text-slate-600">
                    {item.reason}
                  </p>

                </div>
              )}

            </div>
          ))
        )}

      </div>
    </section>
  );
}

export default RequirementTable;