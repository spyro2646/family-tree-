# Android build

`apps/mobile` contains the initial Flutter source and package manifest. Flutter tooling was not available in the inspected environment, and the generated Android Gradle platform directory has not been produced. Install Flutter stable with Android SDK command line tools, then from `apps/mobile` run `flutter create --platforms=android --org com.familyroots .`, review the generated Android application ID and permissions, and run:

```powershell
flutter pub get
flutter analyze
flutter test
flutter build apk --debug --dart-define=API_BASE_URL=https://your-api.example
flutter build apk --release --dart-define=API_BASE_URL=https://your-api.example
```

Expected debug output is `build/app/outputs/flutter-apk/app-debug.apk`. A production release requires a protected signing key and real API URL; no APK has been generated or verified in this environment.

## Hosted debug APK

The workflow at `.github/workflows/android-apk.yml` generates the Android platform files on GitHub's runner, builds the debug APK, and uploads it as the `familyroots-debug-apk` artifact. Push this repository to GitHub, then run **Actions → Android debug APK → Run workflow**. Download the artifact from the completed run. On each commit touching `apps/mobile`, it also runs automatically on `main` or `master`.

To make the installed app connect to a deployed backend, set the repository Actions variable `API_BASE_URL` to that API's HTTPS base URL. Without that configuration, the app uses the Android emulator's local API address.
