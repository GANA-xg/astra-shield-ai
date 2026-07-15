import axios from "axios";

const api = axios.create({
  baseURL: process.env.NEXT_PUBLIC_API_URL ?? "http://127.0.0.1:8000",
});

export async function detectCurrency(file: File) {
  const formData = new FormData();

  formData.append("file", file);

  const response = await api.post(
    "/currency/predict",
    formData
  );

  return response.data;
}