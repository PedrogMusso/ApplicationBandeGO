import axios from "axios";

export const api = axios.create({
  baseURL: "https://fvxd5ssage.execute-api.us-east-1.amazonaws.com/dev",
  timeout: 10000,
  headers: {
    "Content-Type": "application/json",
  },
});
