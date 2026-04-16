package com.studenthelper.app;

import android.annotation.SuppressLint;
import android.app.AlertDialog;
import android.content.DialogInterface;
import android.graphics.Bitmap;
import android.os.Bundle;
import android.view.KeyEvent;
import android.view.View;
import android.webkit.WebChromeClient;
import android.webkit.WebResourceError;
import android.webkit.WebResourceRequest;
import android.webkit.WebSettings;
import android.webkit.WebView;
import android.webkit.WebViewClient;
import android.widget.ProgressBar;

import androidx.appcompat.app.AppCompatActivity;
import androidx.swiperefreshlayout.widget.SwipeRefreshLayout;

public class MainActivity extends AppCompatActivity {
    
    private WebView webView;
    private ProgressBar progressBar;
    private SwipeRefreshLayout swipeRefreshLayout;
    
    // URL вашего проекта
    // ДЛЯ ЭМУЛЯТОРА: "http://10.0.2.2:8000"
    // ДЛЯ РЕАЛЬНОГО УСТРОЙСТВА: "http://ВАШ_IP:8000"
    // ДЛЯ PRODUCTION: "https://flurisrv.ru"
    private static final String BASE_URL = "http://95.31.234.101";
    
    @SuppressLint("SetJavaScriptEnabled")
    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);
        
        // Инициализация компонентов
        webView = findViewById(R.id.webView);
        progressBar = findViewById(R.id.progressBar);
        swipeRefreshLayout = findViewById(R.id.swipeRefreshLayout);
        
        // Настройка WebView
        setupWebView();
        
        // Настройка SwipeRefresh
        setupSwipeRefresh();
        
        // Загрузка URL
        webView.loadUrl(BASE_URL);
    }
    
    @SuppressLint("SetJavaScriptEnabled")
    private void setupWebView() {
        WebSettings webSettings = webView.getSettings();
        
        // Включаем JavaScript
        webSettings.setJavaScriptEnabled(true);
        
        // Включаем поддержку localStorage
        webSettings.setDomStorageEnabled(true);
        
        // Разрешаем доступ к файлам
        webSettings.setAllowFileAccess(true);
        webSettings.setAllowContentAccess(true);
        
        // Включаем зум
        webSettings.setSupportZoom(true);
        webSettings.setBuiltInZoomControls(true);
        webSettings.setDisplayZoomControls(false);
        
        // Настройка кеша
        webSettings.setCacheMode(WebSettings.LOAD_DEFAULT);
        
        // Поддержка viewport
        webSettings.setUseWideViewPort(true);
        webSettings.setLoadWithOverviewMode(true);
        
        // Поддержка mixed content
        webSettings.setMixedContentMode(WebSettings.MIXED_CONTENT_ALWAYS_ALLOW);
        
        // WebViewClient для обработки навигации
        webView.setWebViewClient(new WebViewClient() {
            @Override
            public void onPageStarted(WebView view, String url, Bitmap favicon) {
                super.onPageStarted(view, url, favicon);
                progressBar.setVisibility(View.VISIBLE);
            }
            
            @Override
            public void onPageFinished(WebView view, String url) {
                super.onPageFinished(view, url);
                progressBar.setVisibility(View.GONE);
                swipeRefreshLayout.setRefreshing(false);
            }
            
            @Override
            public void onReceivedError(WebView view, WebResourceRequest request, 
                                       WebResourceError error) {
                super.onReceivedError(view, request, error);
                progressBar.setVisibility(View.GONE);
                swipeRefreshLayout.setRefreshing(false);
                
                if (request.isForMainFrame()) {
                    String errorMessage = "Неизвестная ошибка";
                    String errorType = "Ошибка подключения";
                    int errorCode = -1;
                    
                    if (android.os.Build.VERSION.SDK_INT >= android.os.Build.VERSION_CODES.M) {
                        errorMessage = error.getDescription().toString();
                        errorCode = error.getErrorCode();
                        
                        switch (errorCode) {
                            case WebViewClient.ERROR_HOST_LOOKUP:
                                errorType = "Сервер не найден";
                                break;
                            case WebViewClient.ERROR_CONNECT:
                                errorType = "Не удалось подключиться к серверу";
                                break;
                            case WebViewClient.ERROR_TIMEOUT:
                                errorType = "Превышено время ожидания";
                                break;
                            case WebViewClient.ERROR_FAILED_SSL_HANDSHAKE:
                                errorType = "Ошибка SSL";
                                break;
                            case WebViewClient.ERROR_IO:
                                errorType = "Ошибка ввода-вывода";
                                break;
                            default:
                                errorType = "Код ошибки: " + errorCode;
                                break;
                        }
                    }
                    
                    loadErrorPage(errorType, errorMessage);
                }
            }
            
            @Override
            public boolean shouldOverrideUrlLoading(WebView view, WebResourceRequest request) {
                // Оставляем навигацию внутри WebView
                view.loadUrl(request.getUrl().toString());
                return true;
            }
        });
        
        // WebChromeClient для прогресс-бара
        webView.setWebChromeClient(new WebChromeClient() {
            @Override
            public void onProgressChanged(WebView view, int newProgress) {
                super.onProgressChanged(view, newProgress);
                progressBar.setProgress(newProgress);
            }
        });
    }
    
    private void setupSwipeRefresh() {
        swipeRefreshLayout.setColorSchemeResources(
            R.color.purple_500,
            R.color.purple_700,
            R.color.teal_200
        );
        
        swipeRefreshLayout.setOnRefreshListener(new SwipeRefreshLayout.OnRefreshListener() {
            @Override
            public void onRefresh() {
                webView.reload();
            }
        });
    }
    
    private void loadErrorPage(String errorType, String errorDescription) {
        String errorHtml = "<!DOCTYPE html>" +
                "<html>" +
                "<head>" +
                "    <meta charset='UTF-8'>" +
                "    <meta name='viewport' content='width=device-width, initial-scale=1.0'>" +
                "    <style>" +
                "        body {" +
                "            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;" +
                "            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);" +
                "            color: white;" +
                "            display: flex;" +
                "            justify-content: center;" +
                "            align-items: center;" +
                "            min-height: 100vh;" +
                "            margin: 0;" +
                "            padding: 20px;" +
                "            box-sizing: border-box;" +
                "        }" +
                "        .container {" +
                "            text-align: center;" +
                "            max-width: 400px;" +
                "        }" +
                "        .icon {" +
                "            font-size: 64px;" +
                "            margin-bottom: 20px;" +
                "        }" +
                "        h1 {" +
                "            font-size: 24px;" +
                "            margin: 0 0 10px 0;" +
                "        }" +
                "        .error-type {" +
                "            font-size: 18px;" +
                "            margin: 10px 0;" +
                "            opacity: 0.9;" +
                "        }" +
                "        .error-details {" +
                "            font-size: 14px;" +
                "            margin: 20px 0;" +
                "            opacity: 0.8;" +
                "            background: rgba(255,255,255,0.1);" +
                "            padding: 15px;" +
                "            border-radius: 10px;" +
                "        }" +
                "        button {" +
                "            background: white;" +
                "            color: #667eea;" +
                "            border: none;" +
                "            padding: 15px 40px;" +
                "            font-size: 16px;" +
                "            font-weight: bold;" +
                "            border-radius: 25px;" +
                "            cursor: pointer;" +
                "            margin-top: 20px;" +
                "            box-shadow: 0 4px 15px rgba(0,0,0,0.2);" +
                "        }" +
                "    </style>" +
                "</head>" +
                "<body>" +
                "    <div class='container'>" +
                "        <div class='icon'>⚠️</div>" +
                "        <h1>Приложение недоступно</h1>" +
                "        <div class='error-type'>" + errorType + "</div>" +
                "        <div class='error-details'>" + errorDescription + "</div>" +
                "        <p>Проверьте подключение к интернету или попробуйте позже</p>" +
                "        <button onclick='window.location.reload()'>Повторить попытку</button>" +
                "    </div>" +
                "</body>" +
                "</html>";
        
        webView.loadDataWithBaseURL(null, errorHtml, "text/html", "UTF-8", null);
    }
    
    @Override
    public boolean onKeyDown(int keyCode, KeyEvent event) {
        // Обработка кнопки "Назад"
        if (keyCode == KeyEvent.KEYCODE_BACK && webView.canGoBack()) {
            webView.goBack();
            return true;
        }
        return super.onKeyDown(keyCode, event);
    }
    
    @Override
    protected void onResume() {
        super.onResume();
        webView.onResume();
    }
    
    @Override
    protected void onPause() {
        super.onPause();
        webView.onPause();
    }
    
    @Override
    protected void onDestroy() {
        if (webView != null) {
            webView.destroy();
        }
        super.onDestroy();
    }
}
