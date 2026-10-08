// Tokens live in localStorage so a refresh keeps you logged in.
const KEY = "nb_tokens";

export const getTokens = () => {
  try {
    return JSON.parse(localStorage.getItem(KEY) || "null");
  } catch {
    return null;
  }
};
export const saveTokens = (tokens) => localStorage.setItem(KEY, JSON.stringify(tokens));
export const clearTokens = () => localStorage.removeItem(KEY);
export const TOKEN_KEY = KEY;
