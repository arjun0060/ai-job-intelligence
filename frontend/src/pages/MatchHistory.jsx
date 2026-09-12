import { useEffect, useState } from "react";
import { useParams } from "react-router-dom";

import { getMatchesByResume } from "../services/api";
import MatchCard from "../components/MatchCard";


function MatchHistory() {
  const { resumeId } = useParams();

  const [matches, setMatches] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);


  useEffect(() => {
    const loadMatches = async () => {
      try {
        setLoading(true);
        setError(null);

        const data = await getMatchesByResume(
          resumeId
        );

        setMatches(data.matches || []);
      } catch (err) {
        console.error(err);

        setError(
          err.response?.data?.detail ||
          "Failed to load job matches."
        );
      } finally {
        setLoading(false);
      }
    };


    if (resumeId) {
      loadMatches();
    }
  }, [resumeId]);


  if (loading) {
    return (
      <div className="flex min-h-screen items-center justify-center bg-slate-50">
        <p className="text-sm text-slate-500">
          Loading job matches...
        </p>
      </div>
    );
  }


  if (error) {
    return (
      <div className="flex min-h-screen items-center justify-center bg-slate-50">

        <div className="rounded-xl border border-red-200 bg-white p-6 text-center shadow-sm">

          <h2 className="font-semibold text-red-600">
            Unable to load matches
          </h2>

          <p className="mt-2 text-sm text-slate-500">
            {error}
          </p>

        </div>

      </div>
    );
  }


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


      {/* Main */}
      <main className="mx-auto max-w-5xl px-6 py-8">

        <section className="mb-8">

        <div className="flex flex-col justify-between gap-5 md:flex-row md:items-end">

            <div>

            <p className="text-sm font-medium text-indigo-600">
                Match History
            </p>

            <h2 className="mt-1 text-3xl font-bold text-slate-900">
                Your Job Matches
            </h2>

            <p className="mt-2 max-w-2xl text-sm leading-6 text-slate-500">
                AI-powered compatibility analysis of your resume
                against the jobs you've evaluated.
            </p>

            </div>

            <div className="rounded-xl border border-slate-200 bg-white px-5 py-3 shadow-sm">

            <p className="text-xs font-medium uppercase tracking-wide text-slate-400">
                Total Matches
            </p>

            <p className="mt-1 text-2xl font-bold text-slate-900">
                {matches.length}
            </p>

            </div>

        </div>

        <p className="mt-4 text-xs text-slate-400">
            Resume: {resumeId}
        </p>

        </section>

        {/* Summary */}
        <section className="mb-6 rounded-xl border border-slate-200 bg-white p-5 shadow-sm">

          <div className="flex items-center justify-between">

            <div>
              <p className="text-sm text-slate-500">
                Total Matches
              </p>

              <p className="mt-1 text-2xl font-bold text-slate-900">
                {matches.length}
              </p>
            </div>

            <div className="rounded-lg bg-indigo-50 px-4 py-3 text-sm font-medium text-indigo-600">
              Ranked by match score
            </div>

          </div>

        </section>


        {/* Matches */}
        <section className="space-y-4">

          {matches.length === 0 ? (
            <div className="rounded-xl border border-slate-200 bg-white p-10 text-center shadow-sm">

              <h3 className="font-semibold text-slate-900">
                No matches found
              </h3>

              <p className="mt-2 text-sm text-slate-500">
                Analyze a resume against a job to create
                your first match.
              </p>

            </div>
          ) : (
            matches.map((match, index) => (
            <MatchCard
                key={match.id}
                match={match}
                rank={index + 1}
            />
            ))
          )}

        </section>

      </main>

    </div>
  );
}


export default MatchHistory;