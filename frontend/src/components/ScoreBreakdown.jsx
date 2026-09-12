function ScoreBreakdown({ breakdown }) {
  if (!breakdown) {
    return null;
  }

  const categories = [
    {
      key: "required",
      label: "Required",
    },
    {
      key: "technology",
      label: "Technology",
    },
    {
      key: "preferred",
      label: "Preferred",
    },
  ];

  return (
    <div className="rounded-xl border border-slate-200 bg-white p-6 shadow-sm">
      <div className="mb-5">
        <h2 className="text-lg font-semibold text-slate-900">
          Score Breakdown
        </h2>

        <p className="mt-1 text-sm text-slate-500">
          How the final match score was calculated
        </p>
      </div>

      <div className="space-y-5">
        {categories.map((category) => {
          const item = breakdown[category.key];

          if (!item) {
            return null;
          }

          return (
            <div key={category.key}>
              <div className="mb-2 flex items-center justify-between">
                <span className="text-sm font-medium text-slate-700">
                  {category.label}
                </span>

                <span className="text-sm font-semibold text-slate-900">
                  {Number(item.score).toFixed(2)}%
                </span>
              </div>

              <div className="h-2 overflow-hidden rounded-full bg-slate-100">
                <div
                  className="h-full rounded-full bg-indigo-500"
                  style={{
                    width: `${Math.min(
                      Math.max(item.score, 0),
                      100
                    )}%`,
                  }}
                />
              </div>

              <div className="mt-2 flex justify-between text-xs text-slate-400">
                <span>
                  Weight:{" "}
                  {(item.effective_weight * 100).toFixed(0)}%
                </span>

                <span>
                  Contribution:{" "}
                  {Number(item.contribution).toFixed(2)}
                </span>
              </div>
            </div>
          );
        })}
      </div>

      <div className="mt-6 border-t border-slate-100 pt-5">
        <div className="flex items-center justify-between">
          <span className="font-medium text-slate-700">
            Final Score
          </span>

          <span className="text-2xl font-bold text-indigo-600">
            {Number(
              breakdown.final_score ?? 0
            ).toFixed(2)}%
          </span>
        </div>
      </div>
    </div>
  );
}

export default ScoreBreakdown;