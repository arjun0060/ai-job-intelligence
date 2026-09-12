function ScoreCard({
  title,
  score,
  description,
}) {
  return (
    <div className="rounded-xl border border-slate-200 bg-white p-5 shadow-sm">
      <p className="text-sm font-medium text-slate-500">
        {title}
      </p>

      <div className="mt-2 flex items-end gap-1">
        <span className="text-3xl font-bold text-slate-900">
          {Number(score).toFixed(2)}
        </span>

        <span className="mb-1 text-sm text-slate-500">
          %
        </span>
      </div>

      {description && (
        <p className="mt-2 text-xs text-slate-500">
          {description}
        </p>
      )}
    </div>
  );
}

export default ScoreCard;