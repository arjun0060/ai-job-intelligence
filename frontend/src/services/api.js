import axios from "axios";

const api = axios.create({
  baseURL: "http://127.0.0.1:8000/api/v1",
});

api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem("access_token");

    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }

    return config;
  },
  (error) => Promise.reject(error)
);


api.interceptors.response.use(
  (response) => response,
  (error) => {
    const status = error.response?.status;
    const requestUrl = error.config?.url || "";

    if (
      status === 401 &&
      !requestUrl.includes("/auth/login")
    ) {
      localStorage.removeItem("access_token");

      if (window.location.pathname !== "/login") {
        window.location.href = "/login";
      }
    }

    return Promise.reject(error);
  }
);


export const register = async (email, password) => {
  const response = await api.post("/auth/register", {
    email,
    password,
  });

  return response.data;
};


export const login = async (email, password) => {
  const response = await api.post("/auth/login", {
    email,
    password,
  });

  return response.data;
};


export const getResumes = async () => {
  const response = await api.get("/resumes");

  return response.data;
};


export const uploadResume = async (file) => {
  const formData = new FormData();

  formData.append("file", file);

  const response = await api.post(
    "/resumes/upload",
    formData,
    {
      headers: {
        "Content-Type": "multipart/form-data",
      },
    }
  );

  return response.data;
};


export const extractJob = async (url) => {
  const response = await api.post("/jobs/extract", {
    url,
  });

  return response.data;
};


export const getAnalysisStatus = async (
  resumeId,
  jobId
) => {
  const response = await api.get(
    `/analysis-status/${resumeId}/${jobId}`
  );

  return response.data;
};


export const analyzeMatch = async (
  resumeId,
  jobId
) => {
  const response = await api.post(
    "/matches/analyze",
    {
      resume_id: resumeId,
      job_id: jobId,
    }
  );

  return response.data;
};


export const getMatch = async (matchId) => {
  const response = await api.get(
    `/matches/${matchId}`
  );

  return response.data;
};


export const getMatchesByResume = async (
  resumeId
) => {
  const response = await api.get(
    `/matches/resume/${resumeId}`
  );

  return response.data;
};


export const getMatchesByJob = async (jobId) => {
  const response = await api.get(
    `/matches/job/${jobId}`
  );

  return response.data;
};


export default api;
