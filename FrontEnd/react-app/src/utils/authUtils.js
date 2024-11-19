export const csrfFetch = async (url, options = {}) => {
  // ToDo: maybe beneficial to combine csrfFetch and apiFetch?
  
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

export const apiFetch = async (url, options = {}) => {

  // Extract CSRF and tokens if needed
  const csrfToken = document.cookie
      .split('; ')
      .find(row => row.startsWith('csrf_access_token='))
      ?.split('=')[1];

  // Define default headers // ToDo: Is this vunerable to XSS attacks?
  const defaultHeaders = {
      "X-CSRF-TOKEN": csrfToken,
      "Content-Type": "application/json",
  };

  options.headers = { ...defaultHeaders, ...(options.headers || {}) };
  options.credentials = "include"; // Ensure cookies are included

  let response = await fetch(url, options);

  if (response.status === 401) {
      console.log("Access token expired, attempting refresh...");
      
      // Attempt to refresh the token
      const refreshResponse = await fetch('/refresh', {
          method: 'POST',
          credentials: 'include', // Include cookies for refresh
      });

      if (!refreshResponse.ok) {
          throw new Error('Failed to refresh token. Please log in again.');
      }

      // Retry the original request
      response = await fetch(url, options);
  }

  return response;
};
