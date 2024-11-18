export const prototyping_user_id = "totally4real2uuid";

export const csrfFetch = async (url, options = {}) => {
  const csrfToken = document.cookie
      .split('; ')
      .find(row => row.startsWith('csrf_access_token='))
      ?.split('=')[1];

  const defaultHeaders = {
      "X-CSRF-TOKEN": csrfToken,
      "Content-Type": "application/json",
  };

  options.headers = { ...defaultHeaders, ...(options.headers || {}) };
  options.credentials = "include";

  return fetch(url, options);
};
