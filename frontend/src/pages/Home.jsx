import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { useEffect } from "react";

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
          setError("Resume analysis failed. Please upload the resume again.");
          return;
        }

        if (data.job_status === "failed") {
          setError("Job analysis failed. Please extract the job again.");
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

  const handleResumeSelect = (event) => {
    const selectedId = event.target.value;

    if (!selectedId) {
      setResume(null);
      setJob(null);
      setJobUrl("");
      setAnalysisStatus(null);
      setStep(1);
      setError("");
      return;
    }

    const selectedResume = resumes.find(
      (item) => String(item.id) === selectedId
    );

    if (!selectedResume) return;

    setResume(selectedResume);
    setResumeFile(null);
    setJob(null);
    setJobUrl("");
    setAnalysisStatus(null);
    setStep(2);
    setError("");
  };

  const handleResumeUpload = async () => {
    if (!resumeFile) {
      setError("Please select a PDF resume.");
      return;
    }

    setLoading(true);
    setError("");

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
      setJob(null);
      setJobUrl("");
      setStep(2);
    } catch (err) {
      setError(
        err.response?.data?.detail ||
          "Failed to upload resume."
      );
    } finally {
      setLoading(false);
    }
  };

  const handleJobExtraction = async () => {
    if (!jobUrl.trim()) {
      setError("Please enter a job URL.");
      return;
    }

    setLoading(true);
    setError("");

    try {
      const data = await extractJob(jobUrl);

      setJob(data);
      setAnalysisStatus(null);
      setStep(3);
    } catch (err) {
      setError(
        err.response?.data?.detail ||
          "Failed to extract job."
      );
    } finally {
      setLoading(false);
    }
  };

  const handleMatchAnalysis = async () => {
    if (!resume?.id || !job?.id) {
      setError("Resume or job information is missing.");
      return;
    }

    setLoading(true);
    setError("");

    try {
      const match = await analyzeMatch(
        resume.id,
        job.id
      );

      navigate(`/matches/${match.id}`);
    } catch (err) {
      setError(
        err.response?.data?.detail ||
          "Failed to analyze match."
      );
    } finally {
      setLoading(false);
    }
  };

    useEffect(() => {
    const token = localStorage.getItem("access_token");

    if (!token) {
        navigate("/login");
    }
    }, [navigate]);

  return (
    <div className="min-h-screen bg-slate-50">
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
                navigate(
                  `/resumes/${resume.id}/matches`
                )
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
            Upload your resume, provide a job posting, and
            let the system analyze your requirements,
            technologies, strengths, and gaps.
          </p>
        </div>

        {/* Progress */}
        <div className="mb-8 flex items-center justify-center gap-3">
          <Step number="1" label="Resume" active={step >= 1} />
          <div className="h-px w-12 bg-slate-300" />
          <Step number="2" label="Job" active={step >= 2} />
          <div className="h-px w-12 bg-slate-300" />
          <Step
            number="3"
            label="Analyze"
            active={step >= 3}
          />
        </div>

        {/* Error */}
        {error && (
          <div className="mb-6 rounded-lg border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700">
            {error}
          </div>
        )}

        {/* Resume */}
        <section className="rounded-xl border border-slate-200 bg-white p-6 shadow-sm">
          <div className="mb-5">
            <p className="text-sm font-semibold text-indigo-600">
              STEP 1
            </p>

            <h3 className="mt-1 text-xl font-semibold text-slate-900">
              Choose your resume
            </h3>

            <p className="mt-1 text-sm text-slate-500">
              Select a previous resume or upload a new PDF.
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
                setResumeFile(
                  event.target.files?.[0] || null
                );
                setError("");
              }}
            />

            <span className="text-sm font-medium text-slate-700">
              {resumeFile
                ? resumeFile.name
                : "Click to select a PDF"}
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
            {loading && step === 1
              ? "Uploading..."
              : "Upload Resume"}
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
        <section
          className={`mt-6 rounded-xl border border-slate-200 bg-white p-6 shadow-sm ${
            !resume ? "opacity-50" : ""
          }`}
        >
          <div className="mb-5">
            <p className="text-sm font-semibold text-indigo-600">
              STEP 2
            </p>

            <h3 className="mt-1 text-xl font-semibold text-slate-900">
              Add a job posting
            </h3>

            <p className="mt-1 text-sm text-slate-500">
              Paste the URL of the job you want to analyze.
            </p>
          </div>

          <input
            type="url"
            value={jobUrl}
            disabled={!resume}
            onChange={(event) => {
              setJobUrl(event.target.value);
              setError("");
            }}
            placeholder="https://example.com/jobs/software-engineer"
            className="w-full rounded-lg border border-slate-300 px-4 py-3 text-sm outline-none transition focus:border-indigo-500 focus:ring-2 focus:ring-indigo-100 disabled:bg-slate-100"
          />

          <button
            onClick={handleJobExtraction}
            disabled={loading || !resume || !jobUrl.trim()}
            className="mt-5 w-full rounded-lg bg-slate-900 px-4 py-3 text-sm font-semibold text-white transition hover:bg-slate-800 disabled:cursor-not-allowed disabled:opacity-50"
          >
            {loading && step === 2
              ? "Extracting Job..."
              : "Extract Job"}
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
        <section
          className={`mt-6 rounded-xl border border-slate-200 bg-white p-6 shadow-sm ${
            !job ? "opacity-50" : ""
          }`}
        >
          <div className="mb-5">
            <p className="text-sm font-semibold text-indigo-600">
              STEP 3
            </p>

            <h3 className="mt-1 text-xl font-semibold text-slate-900">
              Analyze your match
            </h3>

            <p className="mt-1 text-sm text-slate-500">
              Compare your resume against the job
              requirements.
            </p>
          </div>

          {job && analysisStatus && !analysisStatus.ready && (
            <div className="mb-4 rounded-lg border border-indigo-100 bg-indigo-50 px-4 py-3 text-sm text-indigo-700">
              {analysisStatus.resume_status === "processing"
                ? "Preparing your resume..."
                : analysisStatus.job_status === "processing"
                  ? "Preparing the job description..."
                  : "Preparing your match..."}
            </div>
          )}

          <button
            onClick={handleMatchAnalysis}
            disabled={
              loading ||
              !job ||
              !analysisStatus?.ready
            }
            className="w-full rounded-lg bg-indigo-600 px-4 py-3 text-sm font-semibold text-white transition hover:bg-indigo-700 disabled:cursor-not-allowed disabled:opacity-50"
          >
            {loading && step === 3
              ? "Analyzing..."
              : analysisStatus?.ready
                ? "Analyze Match"
                : "Preparing Analysis..."}
          </button>
        </section>
      </main>
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