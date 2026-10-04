<div align="center">
<img width="1200" height="475" alt="GHBanner" src="https://ai.google.dev/static/site-assets/images/share-ais-513315318.png" />
</div>

# Run and deploy your AI Studio app

This contains everything you need to run your app locally.

View your app in AI Studio: https://ai.studio/apps/fddd257e-d775-4608-9427-bfc0e768e48e

## Run Locally

**Prerequisites:**  [Android Studio](https://developer.android.com/studio)


1. Open Android Studio
2. Select **Open** and choose the directory containing this project
3. Allow Android Studio to fix any incompatibilities as it imports the project.
4. Create a file named `.env` in the project directory and set `GEMINI_API_KEY` in that file to your Gemini API key (see `.env.example` for an example)
5. Remove this line from the app's `build.gradle.kts` file: `signingConfig = signingConfigs.getByName("debugConfig")`
6. Create a `.env` file in the project root and define your real backend URL. Example:

```
BACKEND_BASE_URL=https://your-backend.example.com/api/v1
GEMINI_API_KEY=MY_GEMINI_API_KEY
```

7. Add Firebase config if you want live Firebase auth:
   - download `google-services.json` from your Firebase console
   - place it in `shopping-ai/app/`
8. Run the app on an emulator or physical device
9. If you have already published your app in AI Studio, please [request upload key reset](https://support.google.com/googleplay/android-developer/answer/9842756#zippy=%2Crequest-an-upload-key-reset) in Google Play Console.
