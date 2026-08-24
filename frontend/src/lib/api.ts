export interface SafeFetchResponse<T = any> {
  success: boolean;
  data?: T;
  error?: string;
  errorType?: string;
}

/**
 * A safe wrapper around fetch that prevents JSON parsing errors or raw exceptions
 * from bleeding into the UI.
 */
export async function safeFetchJson<T = any>(
  url: string,
  options?: RequestInit,
  fallbackErrorMessage: string = 'Something went wrong. Please try again.',
  networkErrorMessage: string = 'Unable to connect to the service. Please check your internet connection and try again.'
): Promise<SafeFetchResponse<T>> {
  try {
    const baseUrl = import.meta.env.VITE_API_BASE_URL || '';
    const fullUrl = url.startsWith('/') ? `${baseUrl}${url}` : url;
    const response = await fetch(fullUrl, options);
    
    try {
      const data = await response.json();
      
      if (!response.ok || data.success === false) {
        return {
          success: false,
          error: data.message || data.error || fallbackErrorMessage,
          errorType: data.status || 'API_ERROR',
          data
        };
      }
      return { success: true, data };
    } catch (parseError) {
      // JSON parsing failed, likely a 500 HTML page or empty response
      return {
        success: false,
        error: fallbackErrorMessage,
        errorType: 'PARSE_ERROR'
      };
    }
  } catch (networkError) {
    // Fetch itself failed (e.g. network disconnected, CORS)
    return {
      success: false,
      error: networkErrorMessage,
      errorType: 'NETWORK_ERROR'
    };
  }
}
