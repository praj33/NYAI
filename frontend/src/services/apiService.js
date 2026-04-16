import { BASE_URL } from "../lib/apiConfig";
import { toast } from "react-hot-toast";

export async function apiRequest(
  endpoint,
  method = "GET",
  body = null
) {
  try {
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), 30000);

    const options = {
      method,
      headers: {
        "Content-Type": "application/json",
      },
      signal: controller.signal
    };

    if (body) {
      options.body = JSON.stringify(body);
    }

    const response = await fetch(`${BASE_URL}${endpoint}`, options);
    clearTimeout(timeoutId);

    if (!response.ok) {
      if (response.status >= 500) {
        toast.error("Backend waking up... please wait.", { duration: 4000 });
      }
      const errorData = await response.json().catch(() => ({}));
      throw new Error(errorData.message || `API request failed with status ${response.status}`);
    }

    return await response.json();
  } catch (error) {
    if (error.name === 'AbortError' || error.message.includes('fetch')) {
      toast.error("Backend waking up... please wait.", { duration: 4000 });
    }
    console.error("Backend Error:", error);
    throw error;
  }
}
