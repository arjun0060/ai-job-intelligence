import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";

import {
  uploadResume,
  getResumes,
  extractJob,
  getAnalysisStatus,
  analyzeMatch,
} from "../services/api";

function Home() {
  const navigate = useNavigate();

  const [resumeFile, setResumeFile] = useState(null);
  const [resume, setResume] = useState(null);
  const [resumes, setResumes] = useState([]);
  const [analysisStatus, setAnalysisStatus] = useState(null);
  const [jobUrl, setJobUrl] = useState("");
  const [job, setJob] = useState(null);

  const [loading, setLoading] = useState(false);
  const [loadingStep, setLoadingStep] = useState(null);
  const [step, setStep] = useState(1);
  const [error, setError] = useState("");

  useEffect(() => {
    const loadResumes = async () => {
      try {
        const data = await getResumes();
        setResumes(data || []);
      } catch (err) {
        console.error("Failed to load previous resumes:", err);
      }
    };

    loadResumes();
  }, []);

  useEffect(() => {
    if (!resume?.id || !job?.id) {
      setAnalysisStatus(null);
      return;
    }

    let cancelled = false;
    let timeoutId = null;

    const checkStatus = async () => {
      try {
        const data = await getAnalysisStatus(resume.id, job.id);

        if (cancelled) return;

        setAnalysisStatus(data);

        if (data.ready) {
          return;
        }

        if (data.resume_status === "failed") {
          setError(
            "Resume analysis failed. Please upload the resume again."
          );
          return;
        }

        if (data.job_status === "failed") {
          setError(
            "Job analysis failed. Please extract the job again."
          );
          return;
        }

        timeoutId = setTimeout(checkStatus, 2000);
      } catch (err) {
        if (!cancelled) {
          console.error("Failed to check analysis status:", err);
          timeoutId = setTimeout(checkStatus, 3000);
        }
      }
    };

    checkStatus();

    return () => {
      cancelled = true;
      if (timeoutId) clearTimeout(timeoutId);
    };
  }, [resume?.id, job?.id]);

  const showError = (message) => {
    setError(message);
  };

  const handleResumeSelect = (event) => {
    const selectedId = event.target.value;

    if (!selectedId) {
      setResume(null);
      setResumeFile(null);
      setAnalysisStatus(null);
      setStep(job ? 2 : 1);
      return;
    }

    const selectedResume = resumes.find(
      (item) => String(item.id) === selectedId
    );

    if (!selectedResume) return;

    setResume(selectedResume);
    setResumeFile(null);
    setAnalysisStatus(null);
    setStep(job ? 3 : 2);
  };

  const handleResumeUpload = async () => {
    if (!resumeFile) {
      showError("Please select a PDF resume.");
      return;
    }

    setLoading(true);
    setLoadingStep("resume");

    try {
      const data = await uploadResume(resumeFile);

      setResume(data);
      setResumes((current) => {
        const exists = current.some((item) => item.id === data.id);
        return exists
          ? current.map((item) => (item.id === data.id ? data : item))
          : [data, ...current];
      });
      setResumeFile(null);
      setAnalysisStatus(null);
      setStep(job ? 3 : 2);
    } catch (err) {
      showError(
        err.response?.data?.detail || "Failed to upload resume."
      );
    } finally {
      setLoading(false);
      setLoadingStep(null);
    }
  };

  const handleJobExtraction = async () => {
    if (!jobUrl.trim()) {
      showError("Please enter a job URL.");
      return;
    }

    setLoading(true);
    setLoadingStep("job");

    try {
      const data = await extractJob(jobUrl);

      setJob(data);
      setAnalysisStatus(null);
      setStep(resume ? 3 : 2);
    } catch (err) {
      showError(
        err.response?.data?.detail || "Failed to extract job."
      );
    } finally {
      setLoading(false);
      setLoadingStep(null);
    }
  };

  const handleMatchAnalysis = async () => {
    if (!resume?.id || !job?.id) {
      showError("Please provide both a resume and a job before analyzing.");
      return;
    }

    if (!analysisStatus?.ready) {
      showError(
        "Resume and job analysis are still being prepared. Please wait a moment."
      );
      return;
    }

    setLoading(true);
    setLoadingStep("match");

    try {
      const match = await analyzeMatch(resume.id, job.id);
      navigate(`/matches/${match.id}`);
    } catch (err) {
      showError(
        err.response?.data?.detail || "Failed to analyze match."
      );
    } finally {
      setLoading(false);
      setLoadingStep(null);
    }
  };

  useEffect(() => {
    const token = localStorage.getItem("access_token");

    if (!token) {
      navigate("/login");
    }
  }, [navigate]);

  const hasResume = Boolean(resume?.id);
  const hasJob = Boolean(job?.id);
  const bothReady = hasResume && hasJob && analysisStatus?.ready;

  const analysisPreparationMessage = () => {
    if (!hasResume && !hasJob) {
      return "Upload or select a resume and extract a job to begin analysis.";
    }

    if (!hasResume) {
      return "Add a resume to prepare the match analysis.";
    }

    if (!hasJob) {
      return "Extract a job posting to prepare the match analysis.";
    }

    if (analysisStatus?.resume_status === "processing") {
      return "Preparing your resume...";
    }

    if (analysisStatus?.job_status === "processing") {
      return "Preparing the job description...";
    }

    return "Preparing your match...";
  };

  const analysisButtonLabel = () => {
    if (loadingStep === "match") return "Analyzing...";
    if (bothReady) return "Analyze Match";
    if (!hasResume && !hasJob) return "Select Resume & Job";
    if (!hasResume) return "Add Resume First";
    if (!hasJob) return "Extract Job First";
    return "Preparing Analysis...";
  };

  return (
    <div className="min-h-screen bg-slate-50">
      {error && (
        <ErrorModal
          message={error}
          onClose={() => setError("")}
        />
      )}

      {/* Header */}
      <header className="border-b border-slate-200 bg-white">
        <div className="mx-auto flex max-w-6xl items-center justify-between px-6 py-5">
          <div>
            <h1 className="text-xl font-bold text-slate-900">
              AI Job Intelligence
            </h1>

            <p className="text-sm text-slate-500">
              Resume-to-job intelligence platform
            </p>
          </div>

          {resume && (
            <button
              onClick={() =>
                navigate(`/resumes/${resume.id}/matches`)
              }
              className="rounded-lg border border-slate-300 px-4 py-2 text-sm font-medium text-slate-700 hover:bg-slate-50"
            >
              Match History
            </button>
          )}

          <button
            onClick={() => {
              localStorage.removeItem("access_token");
              navigate("/login");
            }}
            className="rounded-lg border border-slate-300 px-4 py-2 text-sm font-medium text-slate-700 hover:bg-slate-50"
          >
            Logout
          </button>
        </div>
      </header>

      <main className="mx-auto max-w-4xl px-6 py-12">
        {/* Hero */}
        <div className="mb-10 text-center">
          <h2 className="text-4xl font-bold tracking-tight text-slate-900">
            Find out how well you match a job
          </h2>

          <p className="mx-auto mt-3 max-w-2xl text-slate-500">
            Upload your resume and provide a job posting in either order,
            then let the system analyze your requirements, technologies,
            strengths, and gaps.
          </p>
        </div>

        {/* Progress */}
        <div className="mb-8 flex items-center justify-center gap-3">
          <Step number="1" label="Resume" active={hasResume} />
          <div className="h-px w-12 bg-slate-300" />
          <Step number="2" label="Job" active={hasJob} />
          <div className="h-px w-12 bg-slate-300" />
          <Step number="3" label="Analyze" active={Boolean(bothReady)} />
        </div>

        {/* Resume */}
        <section className="rounded-xl border border-slate-200 bg-white p-6 shadow-sm">
          <div className="mb-5">
            <p className="text-sm font-semibold text-indigo-600">
              RESUME
            </p>

            <h3 className="mt-1 text-xl font-semibold text-slate-900">
              Choose your resume
            </h3>

            <p className="mt-1 text-sm text-slate-500">
              Select a previous resume or upload a new PDF. You can do this
              before or after extracting the job.
            </p>
          </div>

          <select
            value={resume?.id || ""}
            onChange={handleResumeSelect}
            disabled={loading}
            className="w-full rounded-lg border border-slate-300 bg-white px-4 py-3 text-sm outline-none transition focus:border-indigo-500 focus:ring-2 focus:ring-indigo-100 disabled:bg-slate-100"
          >
            <option value="">Select a previously used resume</option>
            {resumes.map((item) => (
              <option key={item.id} value={item.id}>
                {item.original_filename || "Untitled resume"}
              </option>
            ))}
          </select>

          <div className="my-5 flex items-center gap-3">
            <div className="h-px flex-1 bg-slate-200" />
            <span className="text-xs font-medium uppercase tracking-wide text-slate-400">
              Or upload a new resume
            </span>
            <div className="h-px flex-1 bg-slate-200" />
          </div>

          <label className="flex cursor-pointer flex-col items-center justify-center rounded-lg border-2 border-dashed border-slate-300 px-6 py-10 transition hover:border-indigo-400 hover:bg-slate-50">
            <input
              type="file"
              accept=".pdf,application/pdf"
              className="hidden"
              onChange={(event) => {
                setResumeFile(event.target.files?.[0] || null);
              }}
            />

            <span className="text-sm font-medium text-slate-700">
              {resumeFile ? resumeFile.name : "Click to select a PDF"}
            </span>

            <span className="mt-1 text-xs text-slate-400">
              PDF files only
            </span>
          </label>

          <button
            onClick={handleResumeUpload}
            disabled={loading || !resumeFile}
            className="mt-5 w-full rounded-lg bg-slate-900 px-4 py-3 text-sm font-semibold text-white transition hover:bg-slate-800 disabled:cursor-not-allowed disabled:opacity-50"
          >
            {loadingStep === "resume" ? "Uploading..." : "Upload Resume"}
          </button>

          {resume && (
            <div className="mt-4 rounded-lg bg-slate-50 p-4">
              <p className="text-sm font-medium text-slate-900">
                Resume selected
              </p>

              <p className="mt-1 text-xs text-slate-500">
                {resume.original_filename}
              </p>
            </div>
          )}
        </section>

        {/* Job */}
        <section className="mt-6 rounded-xl border border-slate-200 bg-white p-6 shadow-sm">
          <div className="mb-5">
            <p className="text-sm font-semibold text-indigo-600">
              JOB
            </p>

            <h3 className="mt-1 text-xl font-semibold text-slate-900">
              Add a job posting
            </h3>

            <p className="mt-1 text-sm text-slate-500">
              Paste the URL of the job you want to analyze. This can be done
              before or after selecting a resume.
            </p>
          </div>

          <input
            type="url"
            value={jobUrl}
            disabled={loading}
            onChange={(event) => {
              setJobUrl(event.target.value);
            }}
            placeholder="https://example.com/jobs/software-engineer"
            className="w-full rounded-lg border border-slate-300 px-4 py-3 text-sm outline-none transition focus:border-indigo-500 focus:ring-2 focus:ring-indigo-100 disabled:bg-slate-100"
          />

          <button
            onClick={handleJobExtraction}
            disabled={loading || !jobUrl.trim()}
            className="mt-5 w-full rounded-lg bg-slate-900 px-4 py-3 text-sm font-semibold text-white transition hover:bg-slate-800 disabled:cursor-not-allowed disabled:opacity-50"
          >
            {loadingStep === "job" ? "Extracting Job..." : "Extract Job"}
          </button>

          {job && (
            <div className="mt-4 rounded-lg bg-slate-50 p-4">
              <p className="text-sm font-semibold text-slate-900">
                {job.title}
              </p>

              {job.company && (
                <p className="mt-1 text-sm text-slate-500">
                  {job.company}
                </p>
              )}

              {job.location && (
                <p className="mt-1 text-xs text-slate-400">
                  {job.location}
                </p>
              )}
            </div>
          )}
        </section>

        {/* Analysis */}
        <section className="mt-6 rounded-xl border border-slate-200 bg-white p-6 shadow-sm">
          <div className="mb-5">
            <p className="text-sm font-semibold text-indigo-600">
              ANALYSIS
            </p>

            <h3 className="mt-1 text-xl font-semibold text-slate-900">
              Analyze your match
            </h3>

            <p className="mt-1 text-sm text-slate-500">
              Once both items are ready, compare your resume against the job
              requirements.
            </p>
          </div>

          {!bothReady && (
            <div className="mb-4 rounded-lg border border-slate-200 bg-slate-50 px-4 py-3 text-sm text-slate-600">
              {analysisPreparationMessage()}
            </div>
          )}

          <button
            onClick={handleMatchAnalysis}
            disabled={loading || !bothReady}
            className="w-full rounded-lg bg-indigo-600 px-4 py-3 text-sm font-semibold text-white transition hover:bg-indigo-700 disabled:cursor-not-allowed disabled:opacity-50"
          >
            {analysisButtonLabel()}
          </button>
        </section>
      </main>
    </div>
  );
}

function ErrorModal({ message, onClose }) {
  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-900/40 px-4 backdrop-blur-sm">
      <div
        role="alertdialog"
        aria-modal="true"
        aria-labelledby="error-dialog-title"
        className="w-full max-w-md rounded-2xl border border-red-100 bg-white p-6 shadow-2xl"
      >
        <div className="flex items-start gap-4">
          <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-full bg-red-50 text-red-600">
            !
          </div>

          <div className="min-w-0 flex-1">
            <h2
              id="error-dialog-title"
              className="text-lg font-semibold text-slate-900"
            >
              Something went wrong
            </h2>

            <p className="mt-2 text-sm leading-6 text-slate-600">
              {message}
            </p>
          </div>
        </div>

        <button
          onClick={onClose}
          autoFocus
          className="mt-6 w-full rounded-lg bg-slate-900 px-4 py-2.5 text-sm font-semibold text-white transition hover:bg-slate-800"
        >
          Close
        </button>
      </div>
    </div>
  );
}

function Step({ number, label, active }) {
  return (
    <div className="flex items-center gap-2">
      <div
        className={`flex h-8 w-8 items-center justify-center rounded-full text-sm font-semibold ${
          active
            ? "bg-slate-900 text-white"
            : "bg-slate-200 text-slate-500"
        }`}
      >
        {number}
      </div>

      <span className="text-sm font-medium text-slate-600">
        {label}
      </span>
    </div>
  );
}

export default Home;
