# Student Helper - Android App

Android приложение для Student Helper с WebView интеграцией.

## 📱 Особенности

- **WebView** с полной поддержкой JavaScript
- **Splash Screen** с градиентом в стиле бренда
- **Pull-to-Refresh** для обновления страницы
- **Progress Bar** для отслеживания загрузки
- **Offline Detection** с диалогом ошибки
- **Back Navigation** - возврат по истории браузера
- **Storage Support** - localStorage и sessionStorage
- **File Access** - поддержка загрузки файлов

## 🛠️ Технологии

- Java 8
- Android SDK 24+ (Android 7.0+)
- Target SDK 34 (Android 14)
- Material Design Components
- SwipeRefreshLayout

## 🚀 Установка и запуск

### Требования

- Android Studio Hedgehog | 2023.1.1 или новее
- JDK 11 или новее
- Android SDK 34

### Шаги установки

1. **Откройте проект в Android Studio**
   ```
   File -> Open -> выберите папку android/
   ```

2. **Настройте URL сервера**
   
   Откройте `MainActivity.java` и измените `BASE_URL`:
   ```java
   private static final String BASE_URL = "http://10.0.2.2:5173"; // Для эмулятора
   // или
   private static final String BASE_URL = "http://192.168.1.100:5173"; // Для реального устройства
   ```

3. **Синхронизируйте Gradle**
   ```
   File -> Sync Project with Gradle Files
   ```

4. **Запустите приложение**
   - Подключите устройство или запустите эмулятор
   - Нажмите Run (Shift+F10)

## 🔧 Настройка для разработки

### Использование с эмулятором

```java
private static final String BASE_URL = "http://10.0.2.2:5173";
```

`10.0.2.2` - это специальный IP для доступа к localhost хоста из эмулятора.

### Использование с реальным устройством

1. Узнайте IP вашего компьютера:
   ```powershell
   ipconfig
   ```

2. Используйте этот IP:
   ```java
   private static final String BASE_URL = "http://192.168.1.XXX:5173";
   ```

3. Убедитесь, что устройство в той же WiFi сети

### Production конфигурация

Для production сборки измените URL на ваш домен:
```java
private static final String BASE_URL = "https://your-domain.com";
```

## 📦 Сборка APK

### Debug APK

```bash
cd android
./gradlew assembleDebug
```

APK будет в: `app/build/outputs/apk/debug/app-debug.apk`

### Release APK

1. Создайте keystore:
   ```bash
   keytool -genkey -v -keystore student-helper.keystore -alias student-helper -keyalg RSA -keysize 2048 -validity 10000
   ```

2. Создайте `app/keystore.properties`:
   ```properties
   storePassword=your-password
   keyPassword=your-password
   keyAlias=student-helper
   storeFile=../student-helper.keystore
   ```

3. Обновите `app/build.gradle`:
   ```gradle
   android {
       signingConfigs {
           release {
               def keystorePropertiesFile = rootProject.file("keystore.properties")
               def keystoreProperties = new Properties()
               keystoreProperties.load(new FileInputStream(keystorePropertiesFile))
               
               keyAlias keystoreProperties['keyAlias']
               keyPassword keystoreProperties['keyPassword']
               storeFile file(keystoreProperties['storeFile'])
               storePassword keystoreProperties['storePassword']
           }
       }
       buildTypes {
           release {
               signingConfig signingConfigs.release
               minifyEnabled true
               proguardFiles getDefaultProguardFile('proguard-android-optimize.txt'), 'proguard-rules.pro'
           }
       }
   }
   ```

4. Соберите:
   ```bash
   ./gradlew assembleRelease
   ```

## 🎨 Кастомизация

### Изменение иконки

1. Поместите иконку в `app/src/main/res/mipmap-*/`
2. Или используйте Android Studio:
   ```
   Right-click on res -> New -> Image Asset
   ```

### Изменение цветов

Отредактируйте `app/src/main/res/values/colors.xml`:
```xml
<color name="purple_500">#8B5CF6</color>
<color name="teal_200">#3B82F6</color>
```

### Изменение Splash Screen

Отредактируйте `app/src/main/res/layout/activity_splash.xml` и `drawable/splash_gradient.xml`

## 🐛 Решение проблем

### Ошибка "Cleartext HTTP traffic not permitted"

Убедитесь, что в `AndroidManifest.xml` есть:
```xml
android:usesCleartextTraffic="true"
```

### WebView не загружается

1. Проверьте права в `AndroidManifest.xml`
2. Проверьте доступность сервера с устройства
3. Проверьте логи: `View -> Tool Windows -> Logcat`

### Проблемы с JavaScript

Убедитесь, что JavaScript включен:
```java
webSettings.setJavaScriptEnabled(true);
```

## 📄 Структура проекта

```
android/
├── app/
│   ├── src/
│   │   └── main/
│   │       ├── java/com/studenthelper/app/
│   │       │   ├── MainActivity.java       # Основное Activity с WebView
│   │       │   └── SplashActivity.java     # Splash screen
│   │       ├── res/
│   │       │   ├── layout/
│   │       │   │   ├── activity_main.xml   # Layout основного экрана
│   │       │   │   └── activity_splash.xml # Layout splash screen
│   │       │   ├── values/
│   │       │   │   ├── colors.xml          # Цвета приложения
│   │       │   │   ├── strings.xml         # Строковые ресурсы
│   │       │   │   └── themes.xml          # Темы приложения
│   │       │   └── drawable/
│   │       │       └── splash_gradient.xml # Градиент splash screen
│   │       └── AndroidManifest.xml         # Манифест приложения
│   └── build.gradle                        # Конфигурация модуля
├── build.gradle                            # Конфигурация проекта
├── settings.gradle                         # Настройки Gradle
└── gradle.properties                       # Свойства Gradle
```

## 🔐 Permissions

- `INTERNET` - доступ к сети
- `ACCESS_NETWORK_STATE` - проверка состояния сети
- `READ_EXTERNAL_STORAGE` - чтение файлов (для API < 33)
- `WRITE_EXTERNAL_STORAGE` - запись файлов (для API < 33)

## 📱 Системные требования

- **Минимум**: Android 7.0 (API 24)
- **Целевая**: Android 14 (API 34)
- **Рекомендуемая память**: 2GB RAM

## 🚀 Деплой в Google Play

1. Создайте release APK (см. выше)
2. Зарегистрируйтесь в [Google Play Console](https://play.google.com/console)
3. Создайте новое приложение
4. Заполните информацию о приложении
5. Загрузите APK в раздел Production
6. Пройдите процесс ревью

## 📝 Лицензия

MIT License - см. LICENSE в корне проекта
