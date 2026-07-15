import axios from "axios";

const api = axios.create({
  baseURL: "http://127.0.0.1:8000",
});

export async function detectScam(transcript: string) {
  const response = await api.post("/scam/detect", {
    transcript,
  });

  return response.data;
}