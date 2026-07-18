import axios from "axios";

const api = axios.create({
  baseURL: process.env.NEXT_PUBLIC_API_URL ?? "http://127.0.0.1:8000",
});

export async function detectScam(transcript: string) {
  const response = await api.post("/scam/analyze", {
    transcript,
  });

  return response.data;
}