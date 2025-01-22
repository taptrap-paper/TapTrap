# User Study

This directory contains the artefacts of the user study.

> Note: Due to privacy regulations, we are not able to share the raw results of the user study.

## Folder Structure

- `/study_documents`: contains all documents used in the user study (the questionnaires, the information sheets, consent forms, etc.)
- `/KillTheBugs`: the app the user study focused on
- `/WebApp`: the website that the app loads in Levels 1 and 2

## Prepare and run the app

### Website

We use Nginx to serve the website components required for the app. Follow these steps to configure and run the server:

- Replace the placeholders in the configuration file `nginx.conf`
  - `<server_name>`: your server's domain name
  - `<log>`: the path for the access log file
  - `<location>`: the absolute path to the directory containing your `WebApp` folder
- Deploy the WebApp directory to the location specified in `<location>`
- Applay the updated Nginx configuration

### App

- open `/KillTheBugs` with [Android Studio](https://developer.android.com/studio)
- change the value of `webapp` in `res/values/strings.xml` to the URL you are hosting the website on
- run the app
  - the app is optimized for a Pixel 6a running Android 15 (API 35)
  - to test it with this device, create a virtual device in Android Studio