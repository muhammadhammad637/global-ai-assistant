# Global AI Assistant

Streamlit chatbot with English/Roman Urdu intent classification, a global topic catalog,
local conversation history, optional online translation, and an admin-managed FAQ store.

## Run
```
python -m venv .venv
# Windows PowerShell:
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
streamlit run app.py
```

## Admin login and data
- Open the Admin workspace and create a strong password on first use; a salted password hash is saved locally.
- Alternatively configure `GLOBAL_ASSISTANT_ADMIN_PASSWORD` or `.streamlit/secrets.toml` with `[admin]` and `admin_password = "..."`.
- Do not commit passwords or secrets. For public deployment, place the app behind proper hosting authentication and HTTPS.
- Chat history and custom FAQs persist locally in `data/assistant.sqlite3`.
- The admin page supports bulk FAQ CSV import/export and ZIP backup downloads.
- Backups include potentially private chat text; protect them.

## Translation and voice
- The language picker contains 100+ language codes. UI labels are translated offline for English, Urdu, and Hindi.
- Translation of answers into other languages requires a supported provider and its API key.
- Offline chat answers built-in FAQ topics; it is not a general-purpose answer model. To ask broader questions, configure `OPENAI_API_KEY` and explicitly enable **Use online AI** in the sidebar. Prompts are sent to OpenAI and usage may incur charges.
- To enable optional online question/answer translation, set `GOOGLE_TRANSLATE_API_KEY`.
  The user must turn on the toggle; query and answer text are sent to Google Cloud Translation.
- Voice input requires browser speech-recognition support and microphone permission.
- Voice output uses the browser's built-in speech synthesis.
- Creation Studio includes voice input/read-aloud and downloadable text-to-speech. Downloadable MP3 generation requires `OPENAI_API_KEY`.
- The sidebar's module catalog contains 1,000 searchable starter prompts across 25 categories. These are question templates, not 1,000 separate AI models or provider integrations.
- **Everyday tools** adds four working modules: study summaries/quizzes/flashcards; PDF, DOCX, and text-document summaries/Q&A; offline arithmetic, unit conversion, and date planning; and AI-assisted email, resume, and social-caption drafts. AI-assisted modules require `OPENAI_API_KEY`; uploaded notes/documents are sent to OpenAI only after submission. Scanned PDFs need OCR and are not supported.

## Sign-in and media
- Sign-in uses a single configured OpenID Connect identity provider; see the Sign in workspace for a secrets.toml example.
- Signup and OTP/MFA are handled by that identity provider. The app does not collect third-party OTP codes.
- The social provider list is a planning catalog, not 100 working integrations. Streamlit supports one configured OIDC provider at a time; each real provider needs approved OAuth/OIDC credentials and a registered callback URL.
- Image generation is available when `OPENAI_API_KEY` is configured; calls may incur charges and prompts are sent to the provider.
- The app includes 100 neon-reflection color schemes and 120 locally generated abstract SVG backgrounds, not stock photographs.
- The Creation Studio provides OpenAI-backed text-to-speech and image generation when `OPENAI_API_KEY` is configured.
- Runway Gen-4.5 text-to-video is available when `RUNWAYML_API_SECRET` is configured. Start a task and check its asynchronous status in Creation Studio; Runway usage can incur charges.
- The Instagram insights workspace supports read-only connections to Instagram Professional (Business/Creator) accounts. It uses Meta's Instagram Login and needs `INSTAGRAM_APP_ID`, `INSTAGRAM_APP_SECRET`, and `INSTAGRAM_REDIRECT_URI`. Tokens are kept in the current app session and are not saved to the project database. Only the `instagram_business_basic` and `instagram_business_manage_insights` permissions are requested; posting, comments, and messages are not enabled.
- The chat accepts a catalog of 100+ file extensions, limited to five files of up to 10 MB each. Common text files and images are read locally; other file types are listed/uploadable but their contents are not extracted. Uploaded files are not persisted.
- Projects and agent guidance are stored in the local SQLite database. Agent instructions are applied only in online AI mode.
- The sidebar's module catalog contains 1,000 searchable starter prompts across 25 categories. These are question templates, not 1,000 separate AI models or provider integrations.
- All 120 local SVG backgrounds rotate automatically behind the chat UI on a 12-minute loop; each scene remains for about six seconds. The selected neon palette adds ambient light reflections.
- Do not collect OTP codes yourself; use the configured identity provider's supported MFA flow.
- Video input is text-to-video; image-to-video and other video vendors are not connected.
- Google search ranking cannot be guaranteed. A public domain, crawlable production site, verified ownership, and ongoing SEO are needed.
- Google Play and other store releases require a signed mobile package, developer accounts, privacy disclosures, and review. This Streamlit project is not itself a store-ready mobile app.

### Run the app from Windows CMD
Stop the currently running Streamlit session first. Then double-click `run_assistant.cmd`, or run it from Command Prompt in the project folder:
```
run_assistant.cmd
```
The launcher securely prompts for optional keys without echoing or saving them. Press Enter to skip either key. `OPENAI_API_KEY` enables online AI answers, downloadable speech, and image generation; `RUNWAYML_API_SECRET` enables video generation. Keep the CMD window open while using the app; closing it stops the app and discards the session keys. Provider use may incur charges. Never paste real keys into chat, screenshots, source code, or a committed file.
For Instagram insights, also enter the Instagram App ID and App Secret when prompted. The local redirect URI is `http://localhost:8501/`; add this exact URI to the Meta app's Instagram OAuth redirect settings. For Cloud Run, configure `INSTAGRAM_REDIRECT_URI=https://faqchatbot.com/` and store `INSTAGRAM_APP_SECRET` in Google Secret Manager instead of using the local launcher prompt.

The Instagram integration uses Meta's [Business Login for Instagram](https://developers.facebook.com/documentation/instagram-platform/instagram-api-with-instagram-login/business-login) and [Insights API](https://developers.facebook.com/documentation/instagram-platform/insights). Configure a Business-type Meta app with Instagram Login, request only basic profile and insights, and add your account as a tester during development. Meta review may be required before serving accounts outside the app's own testers.

### Google Cloud Run deployment (Windows CMD)
The repository includes a Dockerfile for Cloud Run and optional PostgreSQL support. Local use remains SQLite; for a hosted deployment, use Cloud SQL PostgreSQL rather than Cloud Run's temporary filesystem.

Prerequisites: install Google Cloud CLI, sign in with an account that can create resources, select a project with billing enabled, and choose a region. Cloud SQL, Cloud Run, Artifact Registry, Cloud Build, and secret storage can incur charges.

In CMD, from the project directory:
```
set PROJECT_ID=your-gcp-project-id
set REGION=us-central1
set SERVICE=global-assistant
set SQL_INSTANCE=global-assistant-db
set SQL_DATABASE=global_assistant
set SQL_USER=assistant_app
gcloud auth login
gcloud config set project %PROJECT_ID%
gcloud services enable run.googleapis.com artifactregistry.googleapis.com cloudbuild.googleapis.com sqladmin.googleapis.com secretmanager.googleapis.com
gcloud artifacts repositories create global-assistant --repository-format=docker --location=%REGION%
```

Create the managed database in the selected region. The sample tier below is a starting point only; choose a size based on the university's workload and budget:
```
gcloud sql instances create %SQL_INSTANCE% --database-version=POSTGRES_16 --region=%REGION% --tier=db-custom-1-3840 --storage-type=SSD --storage-size=20 --storage-auto-increase
gcloud sql databases create %SQL_DATABASE% --instance=%SQL_INSTANCE%
```

Create a dedicated database user using the Cloud Console or an approved password-input workflow. Create Secret Manager secrets for `assistant-db-password` and `global-assistant-admin-password`; do not put secret values in CMD commands or source control. Configure Cloud SQL automated backups and retention before using real user data. Cloud SQL and Cloud Run are billable services.

Create an Auth0 Regular Web Application and add the Auth0 tenant discovery URL and app credentials to a `secrets.toml` file with this structure. The callback URL must use the exact Cloud Run service URL; create the service first, then register its URL in Auth0:
```toml
[auth]
redirect_uri = "https://YOUR-CLOUD-RUN-URL/oauth2callback"
cookie_secret = "GENERATE-A-LONG-RANDOM-SECRET"
client_id = "AUTH0-CLIENT-ID"
client_secret = "AUTH0-CLIENT-SECRET"
server_metadata_url = "https://YOUR_AUTH0_DOMAIN/.well-known/openid-configuration"
client_kwargs = { scope = "openid email profile" }
```

In Auth0, configure the app as a Regular Web Application, enable Authorization Code login, and set its Allowed Callback URL to `https://YOUR-CLOUD-RUN-URL/oauth2callback`. Set the Allowed Logout URL and Web Origin to the service URL too. Upload the TOML configuration to Secret Manager as `global-assistant-auth-config`; do not commit it or put its values in a CMD command.

Then build and deploy the image. Keep the service private for the first deployment; review privacy, access controls, and rate limits before granting public invocation:
```
gcloud sql instances describe %SQL_INSTANCE% --format="value(connectionName)"
gcloud iam service-accounts create global-assistant-runtime
gcloud projects add-iam-policy-binding %PROJECT_ID% --member=serviceAccount:global-assistant-runtime@%PROJECT_ID%.iam.gserviceaccount.com --role=roles/cloudsql.client
gcloud secrets add-iam-policy-binding assistant-db-password --member=serviceAccount:global-assistant-runtime@%PROJECT_ID%.iam.gserviceaccount.com --role=roles/secretmanager.secretAccessor
gcloud secrets add-iam-policy-binding global-assistant-admin-password --member=serviceAccount:global-assistant-runtime@%PROJECT_ID%.iam.gserviceaccount.com --role=roles/secretmanager.secretAccessor
gcloud secrets add-iam-policy-binding global-assistant-auth-config --member=serviceAccount:global-assistant-runtime@%PROJECT_ID%.iam.gserviceaccount.com --role=roles/secretmanager.secretAccessor
gcloud builds submit --tag %REGION%-docker.pkg.dev/%PROJECT_ID%/global-assistant/%SERVICE%:latest
gcloud run deploy %SERVICE% --image=%REGION%-docker.pkg.dev/%PROJECT_ID%/global-assistant/%SERVICE%:latest --region=%REGION% --port=8080 --memory=2Gi --cpu=2 --max=3 --service-account=global-assistant-runtime@%PROJECT_ID%.iam.gserviceaccount.com --add-cloudsql-instances=%PROJECT_ID%:%REGION%:%SQL_INSTANCE% --set-env-vars=GLOBAL_ASSISTANT_DB_HOST=/cloudsql/%PROJECT_ID%:%REGION%:%SQL_INSTANCE%,GLOBAL_ASSISTANT_DB_NAME=%SQL_DATABASE%,GLOBAL_ASSISTANT_DB_USER=%SQL_USER% --set-secrets=GLOBAL_ASSISTANT_DB_PASSWORD=assistant-db-password:latest,GLOBAL_ASSISTANT_ADMIN_PASSWORD=global-assistant-admin-password:latest
```

After creating the service, get its URL, update the Auth0 callback settings and the `redirect_uri` in the secret TOML, then mount that secret file:
```
gcloud run services describe %SERVICE% --region=%REGION% --format="value(status.url)"
gcloud run services update %SERVICE% --region=%REGION% --set-secrets=/app/.streamlit/secrets.toml=global-assistant-auth-config:latest
```

After reviewing the public-facing app and privacy requirements, grant public access only if intended:
```
gcloud run services add-iam-policy-binding %SERVICE% --region=%REGION% --member=allUsers --role=roles/run.invoker
gcloud run services describe %SERVICE% --region=%REGION% --format="value(status.url)"
```

The app's admin console has its own password; the Cloud Run IAM setting controls access to the whole service, not individual app workspaces. When OIDC is configured, app workspaces require sign-in. However, the current project/agent data is shared across signed-in accounts and chat history is visible in the admin console. Do not use this deployment for sensitive multi-tenant data until per-user ownership and authorization are implemented. Configure an HTTPS custom domain, abuse/rate controls, least-privilege access, privacy/terms pages, monitoring, and a recovery plan before sharing with users.

After creating a media secret in Secret Manager, grant the runtime service account access to that secret and enable its environment variable. Run only the matching commands for features you will use:
```
gcloud secrets add-iam-policy-binding openai-api-key --member=serviceAccount:global-assistant-runtime@%PROJECT_ID%.iam.gserviceaccount.com --role=roles/secretmanager.secretAccessor
gcloud run services update %SERVICE% --region=%REGION% --set-secrets=OPENAI_API_KEY=openai-api-key:latest
gcloud secrets add-iam-policy-binding runway-api-secret --member=serviceAccount:global-assistant-runtime@%PROJECT_ID%.iam.gserviceaccount.com --role=roles/secretmanager.secretAccessor
gcloud run services update %SERVICE% --region=%REGION% --set-secrets=RUNWAYML_API_SECRET=runway-api-secret:latest
```

For the Instagram insights workspace, create the `instagram-app-secret` value in Secret Manager using the Cloud Console, grant the runtime service account access, and configure the public Instagram App ID and exact HTTPS OAuth redirect URI:
```
gcloud secrets add-iam-policy-binding instagram-app-secret --member=serviceAccount:global-assistant-runtime@%PROJECT_ID%.iam.gserviceaccount.com --role=roles/secretmanager.secretAccessor
gcloud run services update %SERVICE% --region=%REGION% --update-env-vars=INSTAGRAM_APP_ID=YOUR_INSTAGRAM_APP_ID,INSTAGRAM_REDIRECT_URI=https://faqchatbot.com/ --update-secrets=INSTAGRAM_APP_SECRET=instagram-app-secret:latest
```
Register `https://faqchatbot.com/` as an OAuth redirect URI in the Meta app. Map the verified custom domain to the deployed Cloud Run service and update its DNS records to the values Google provides before expecting that URL to serve this app.

### Native mobile API service
The Flutter app calls a separate authenticated API service. Build and deploy it using the same Cloud SQL instance and runtime service account:
```
set API_SERVICE=global-assistant-api
gcloud iam service-accounts create global-assistant-api-runtime
gcloud projects add-iam-policy-binding %PROJECT_ID% --member=serviceAccount:global-assistant-api-runtime@%PROJECT_ID%.iam.gserviceaccount.com --role=roles/cloudsql.client
gcloud secrets add-iam-policy-binding assistant-db-password --member=serviceAccount:global-assistant-api-runtime@%PROJECT_ID%.iam.gserviceaccount.com --role=roles/secretmanager.secretAccessor
gcloud builds submit --region=%REGION% --config=cloudbuild-api.yaml --substitutions=_IMAGE=%REGION%-docker.pkg.dev/%PROJECT_ID%/global-assistant/%API_SERVICE%:latest .
gcloud run deploy %API_SERVICE% --image=%REGION%-docker.pkg.dev/%PROJECT_ID%/global-assistant/%API_SERVICE%:latest --region=%REGION% --port=8080 --memory=2Gi --cpu=2 --max=3 --service-account=global-assistant-api-runtime@%PROJECT_ID%.iam.gserviceaccount.com --allow-unauthenticated --add-cloudsql-instances=%PROJECT_ID%:%REGION%:%SQL_INSTANCE% --set-env-vars=AUTH0_DOMAIN=YOUR_AUTH0_DOMAIN,GLOBAL_ASSISTANT_DB_HOST=/cloudsql/%PROJECT_ID%:%REGION%:%SQL_INSTANCE%,GLOBAL_ASSISTANT_DB_NAME=%SQL_DATABASE%,GLOBAL_ASSISTANT_DB_USER=%SQL_USER% --set-secrets=GLOBAL_ASSISTANT_DB_PASSWORD=assistant-db-password:latest
gcloud run services describe %API_SERVICE% --region=%REGION% --format="value(status.url)"
```

The API requires a bearer token; it verifies each caller with Auth0's `/userinfo` endpoint, scopes chat history and video jobs to the Auth0 subject, and returns a clear authentication error when Auth0 is unavailable. Routes include `/api/chat`, `/api/history/{conversation_id}`, `/api/media/speech`, `/api/media/video`, and `/api/media/video/{task_id}`. Attach the optional OpenAI/Runway secrets to the API service as well if mobile voice/video creation is enabled, and grant the API service account access only to the secrets it uses. Add rate and cost controls before public use.

Build/run Flutter after installing its SDK and scaffolding the native Android/iOS folders; follow [mobile/README.md](./mobile/README.md). Provide the API service URL and Auth0 Native app's public client ID at build time. Keep Auth0 client secrets, Cloud SQL passwords, OpenAI keys, and Runway keys out of the Flutter app; mobile binaries cannot safely store server secrets.

### Google Search, identity providers, and app stores
- A CMD command cannot create provider accounts, approve OAuth apps, buy a domain, or publish a store app. Those steps require the project owner to sign in, accept provider terms, configure billing/verification, and supply authorized credentials.
- For Google Search, publish a crawlable public website on a domain you control, verify the domain in Google Search Console, submit a sitemap, and maintain useful public pages. Indexing and ranking are controlled by Google and cannot be guaranteed by code.
- A Google Play or other store listing needs a separately packaged mobile/PWA client, developer account, app signing, privacy disclosures, screenshots, and store review. This Streamlit interface does not currently produce an Android/iOS package.
- The app connects to Auth0 through one OIDC configuration. Auth0 can broker supported social connections, but each connection needs its own approved provider credentials/settings and must be enabled in the Auth0 dashboard. The catalog is not 100 active connections; availability and limits depend on Auth0's current plan and each upstream provider.

## Proposed module catalog
The application includes a downloadable catalog of 1,000 distinct topic/audience entries
across 25 categories. It is a browsable proposal, not 1,000 verified knowledge bases.
Country-specific medical, legal, financial, and travel facts should be checked against
reliable local sources before being presented as authoritative advice.
Admin also offers 100 security, 100 frontend, and 100 backend checklist ideas.
