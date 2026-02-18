// Unity API Manager for CommunityMycelium Django Backend
// This example demonstrates how to authenticate and interact with the Django REST API

using System;
using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using UnityEngine.Networking;

/// <summary>
/// User data model matching Django User serializer
/// </summary>
[System.Serializable]
public class UserData
{
    public int id;
    public string username;
    public string email;
    public string full_name;
    public string user_location;
    public bool view_members;
    public bool view_public;
    public bool is_admin;
}

/// <summary>
/// Login response from API
/// </summary>
[System.Serializable]
public class LoginResponse
{
    public string access;
    public string refresh;
    public UserData user;
}

/// <summary>
/// Registration request data
/// </summary>
[System.Serializable]
public class RegisterRequest
{
    public string username;
    public string email;
    public string full_name;
    public string password;
    public string confirm_password;
}

/// <summary>
/// Token refresh response
/// </summary>
[System.Serializable]
public class TokenRefreshResponse
{
    public string access;
}

/// <summary>
/// Login request data
/// </summary>
[System.Serializable]
public class LoginRequest
{
    public string username;
    public string password;
}

/// <summary>
/// Logout request data
/// </summary>
[System.Serializable]
public class LogoutRequest
{
    public string refresh;
}

/// <summary>
/// Refresh token request data
/// </summary>
[System.Serializable]
public class RefreshRequest
{
    public string refresh;
}

/// <summary>
/// API Manager for handling authentication and requests to Django backend
/// </summary>
public class UnityAPIManager : MonoBehaviour
{
    // Singleton instance
    public static UnityAPIManager Instance { get; private set; }

    // API Configuration
    private const string API_BASE_URL = "http://localhost:8000/api";
    
    // Token storage keys
    private const string ACCESS_TOKEN_KEY = "access_token";
    private const string REFRESH_TOKEN_KEY = "refresh_token";
    
    // Cached tokens
    private string accessToken;
    private string refreshToken;
    
    // Current user data
    public UserData CurrentUser { get; private set; }
    
    // Events
    public event Action<UserData> OnLoginSuccess;
    public event Action<string> OnLoginFailed;
    public event Action OnLogoutSuccess;

    private void Awake()
    {
        // Singleton pattern
        if (Instance == null)
        {
            Instance = this;
            DontDestroyOnLoad(gameObject);
            LoadTokens();
        }
        else
        {
            Destroy(gameObject);
        }
    }

    #region Token Management

    /// <summary>
    /// Load tokens from PlayerPrefs (you may want to use more secure storage)
    /// </summary>
    private void LoadTokens()
    {
        accessToken = PlayerPrefs.GetString(ACCESS_TOKEN_KEY, null);
        refreshToken = PlayerPrefs.GetString(REFRESH_TOKEN_KEY, null);
    }

    /// <summary>
    /// Save tokens to PlayerPrefs
    /// </summary>
    private void SaveTokens(string access, string refresh)
    {
        accessToken = access;
        refreshToken = refresh;
        
        PlayerPrefs.SetString(ACCESS_TOKEN_KEY, access);
        PlayerPrefs.SetString(REFRESH_TOKEN_KEY, refresh);
        PlayerPrefs.Save();
    }

    /// <summary>
    /// Clear stored tokens
    /// </summary>
    private void ClearTokens()
    {
        accessToken = null;
        refreshToken = null;
        
        PlayerPrefs.DeleteKey(ACCESS_TOKEN_KEY);
        PlayerPrefs.DeleteKey(REFRESH_TOKEN_KEY);
        PlayerPrefs.Save();
    }

    /// <summary>
    /// Check if user is authenticated
    /// </summary>
    public bool IsAuthenticated()
    {
        return !string.IsNullOrEmpty(accessToken);
    }

    #endregion

    #region Authentication

    /// <summary>
    /// Login with username and password
    /// </summary>
    public void Login(string username, string password, Action<UserData> onSuccess = null, Action<string> onError = null)
    {
        StartCoroutine(LoginCoroutine(username, password, onSuccess, onError));
    }

    private IEnumerator LoginCoroutine(string username, string password, Action<UserData> onSuccess, Action<string> onError)
    {
        string url = $"{API_BASE_URL}/auth/login/";
        
        // Create login request data
        var loginData = new LoginRequest
        {
            username = username,
            password = password
        };
        
        string jsonData = JsonUtility.ToJson(loginData);
        Debug.Log($"Sending login request to {url} with data: {jsonData}");
        
        using (UnityWebRequest request = new UnityWebRequest(url, "POST"))
        {
            byte[] bodyRaw = System.Text.Encoding.UTF8.GetBytes(jsonData);
            request.uploadHandler = new UploadHandlerRaw(bodyRaw);
            request.downloadHandler = new DownloadHandlerBuffer();
            request.SetRequestHeader("Content-Type", "application/json");
            
            yield return request.SendWebRequest();
            
            if (request.result == UnityWebRequest.Result.Success)
            {
                // Parse response
                LoginResponse response = JsonUtility.FromJson<LoginResponse>(request.downloadHandler.text);
                
                // Save tokens
                SaveTokens(response.access, response.refresh);
                
                // Store user data
                CurrentUser = response.user;
                
                // Invoke success callbacks
                OnLoginSuccess?.Invoke(response.user);
                onSuccess?.Invoke(response.user);
                
                Debug.Log($"Login successful! Welcome {response.user.full_name}");
            }
            else
            {
                string errorMessage = $"Login failed: {request.error}";
                string responseText = request.downloadHandler?.text ?? "No response";
                Debug.LogError($"{errorMessage}\nResponse: {responseText}");
                
                OnLoginFailed?.Invoke(errorMessage);
                onError?.Invoke(errorMessage);
            }
        }
    }

    /// <summary>
    /// Register a new user
    /// </summary>
    public void Register(string username, string email, string fullName, string password, 
        Action<UserData> onSuccess = null, Action<string> onError = null)
    {
        StartCoroutine(RegisterCoroutine(username, email, fullName, password, onSuccess, onError));
    }

    private IEnumerator RegisterCoroutine(string username, string email, string fullName, string password,
        Action<UserData> onSuccess, Action<string> onError)
    {
        string url = $"{API_BASE_URL}/auth/register/";
        
        var registerData = new RegisterRequest
        {
            username = username,
            email = email,
            full_name = fullName,
            password = password,
            confirm_password = password
        };
        
        string jsonData = JsonUtility.ToJson(registerData);
        
        using (UnityWebRequest request = new UnityWebRequest(url, "POST"))
        {
            byte[] bodyRaw = System.Text.Encoding.UTF8.GetBytes(jsonData);
            request.uploadHandler = new UploadHandlerRaw(bodyRaw);
            request.downloadHandler = new DownloadHandlerBuffer();
            request.SetRequestHeader("Content-Type", "application/json");
            
            yield return request.SendWebRequest();
            
            if (request.result == UnityWebRequest.Result.Success)
            {
                LoginResponse response = JsonUtility.FromJson<LoginResponse>(request.downloadHandler.text);
                
                SaveTokens(response.access, response.refresh);
                CurrentUser = response.user;
                
                onSuccess?.Invoke(response.user);
                Debug.Log($"Registration successful! Welcome {response.user.full_name}");
            }
            else
            {
                string errorMessage = $"Registration failed: {request.error}";
                Debug.LogError(errorMessage);
                onError?.Invoke(errorMessage);
            }
        }
    }

    /// <summary>
    /// Logout and clear tokens
    /// </summary>
    public void Logout(Action onSuccess = null)
    {
        StartCoroutine(LogoutCoroutine(onSuccess));
    }

    private IEnumerator LogoutCoroutine(Action onSuccess)
    {
        string url = $"{API_BASE_URL}/auth/logout/";
        
        var logoutData = new LogoutRequest
        {
            refresh = refreshToken
        };
        
        string jsonData = JsonUtility.ToJson(logoutData);
        
        using (UnityWebRequest request = new UnityWebRequest(url, "POST"))
        {
            byte[] bodyRaw = System.Text.Encoding.UTF8.GetBytes(jsonData);
            request.uploadHandler = new UploadHandlerRaw(bodyRaw);
            request.downloadHandler = new DownloadHandlerBuffer();
            request.SetRequestHeader("Content-Type", "application/json");
            request.SetRequestHeader("Authorization", $"Bearer {accessToken}");
            
            yield return request.SendWebRequest();
            
            // Clear tokens regardless of response
            ClearTokens();
            CurrentUser = null;
            
            OnLogoutSuccess?.Invoke();
            onSuccess?.Invoke();
            
            Debug.Log("Logout successful");
        }
    }

    /// <summary>
    /// Refresh the access token
    /// </summary>
    private IEnumerator RefreshTokenCoroutine(Action<bool> callback)
    {
        string url = $"{API_BASE_URL}/auth/refresh/";
        
        var refreshData = new RefreshRequest
        {
            refresh = refreshToken
        };
        
        string jsonData = JsonUtility.ToJson(refreshData);
        
        using (UnityWebRequest request = new UnityWebRequest(url, "POST"))
        {
            byte[] bodyRaw = System.Text.Encoding.UTF8.GetBytes(jsonData);
            request.uploadHandler = new UploadHandlerRaw(bodyRaw);
            request.downloadHandler = new DownloadHandlerBuffer();
            request.SetRequestHeader("Content-Type", "application/json");
            
            yield return request.SendWebRequest();
            
            if (request.result == UnityWebRequest.Result.Success)
            {
                TokenRefreshResponse response = JsonUtility.FromJson<TokenRefreshResponse>(request.downloadHandler.text);
                SaveTokens(response.access, refreshToken);
                callback?.Invoke(true);
                Debug.Log("Token refreshed successfully");
            }
            else
            {
                Debug.LogError("Failed to refresh token. User needs to log in again.");
                ClearTokens();
                callback?.Invoke(false);
            }
        }
    }

    #endregion

    #region API Requests

    /// <summary>
    /// Generic GET request with authentication
    /// </summary>
    public void Get<T>(string endpoint, Action<T> onSuccess, Action<string> onError)
    {
        StartCoroutine(GetCoroutine(endpoint, onSuccess, onError));
    }

    private IEnumerator GetCoroutine<T>(string endpoint, Action<T> onSuccess, Action<string> onError)
    {
        string url = $"{API_BASE_URL}/{endpoint}";
        
        using (UnityWebRequest request = UnityWebRequest.Get(url))
        {
            request.SetRequestHeader("Authorization", $"Bearer {accessToken}");
            
            yield return request.SendWebRequest();
            
            if (request.result == UnityWebRequest.Result.Success)
            {
                T response = JsonUtility.FromJson<T>(request.downloadHandler.text);
                onSuccess?.Invoke(response);
            }
            else if (request.responseCode == 401)
            {
                // Token expired, try to refresh
                bool refreshed = false;
                yield return RefreshTokenCoroutine((success) => refreshed = success);
                
                if (refreshed)
                {
                    // Retry the request
                    yield return GetCoroutine(endpoint, onSuccess, onError);
                }
                else
                {
                    onError?.Invoke("Authentication failed. Please log in again.");
                }
            }
            else
            {
                onError?.Invoke($"Request failed: {request.error}");
            }
        }
    }

    /// <summary>
    /// Generic POST request with authentication
    /// </summary>
    public void Post<T>(string endpoint, object data, Action<T> onSuccess, Action<string> onError)
    {
        StartCoroutine(PostCoroutine(endpoint, data, onSuccess, onError));
    }

    private IEnumerator PostCoroutine<T>(string endpoint, object data, Action<T> onSuccess, Action<string> onError)
    {
        string url = $"{API_BASE_URL}/{endpoint}";
        string jsonData = JsonUtility.ToJson(data);
        
        using (UnityWebRequest request = new UnityWebRequest(url, "POST"))
        {
            byte[] bodyRaw = System.Text.Encoding.UTF8.GetBytes(jsonData);
            request.uploadHandler = new UploadHandlerRaw(bodyRaw);
            request.downloadHandler = new DownloadHandlerBuffer();
            request.SetRequestHeader("Content-Type", "application/json");
            request.SetRequestHeader("Authorization", $"Bearer {accessToken}");
            
            yield return request.SendWebRequest();
            
            if (request.result == UnityWebRequest.Result.Success)
            {
                T response = JsonUtility.FromJson<T>(request.downloadHandler.text);
                onSuccess?.Invoke(response);
            }
            else if (request.responseCode == 401)
            {
                // Token expired, try to refresh
                bool refreshed = false;
                yield return RefreshTokenCoroutine((success) => refreshed = success);
                
                if (refreshed)
                {
                    // Retry the request
                    yield return PostCoroutine(endpoint, data, onSuccess, onError);
                }
                else
                {
                    onError?.Invoke("Authentication failed. Please log in again.");
                }
            }
            else
            {
                onError?.Invoke($"Request failed: {request.error}");
            }
        }
    }

    #endregion
}

// Example usage in another script:
/*
public class LoginUI : MonoBehaviour
{
    public void OnLoginButtonClicked()
    {
        string username = usernameInputField.text;
        string password = passwordInputField.text;
        
        UnityAPIManager.Instance.Login(username, password, 
            onSuccess: (user) => {
                Debug.Log($"Logged in as {user.full_name}");
                // Load main scene or update UI
            },
            onError: (error) => {
                Debug.LogError(error);
                // Show error message to user
            }
        );
    }
    
    public void LoadUserList()
    {
        UnityAPIManager.Instance.Get<UserListResponse>("people/",
            onSuccess: (response) => {
                Debug.Log($"Loaded {response.count} people");
                // Process user list
            },
            onError: (error) => {
                Debug.LogError(error);
            }
        );
    }
}
*/
