# Cloud Deployment Guide - College Mail Guardian

Follow these steps to host your application 24/7 on the cloud for free without losing any data or going to sleep.

---

## Step 1: Push Code to GitHub

1. Open a terminal in the `college_mail_guardian` folder.
2. Initialize Git, add files, and commit:
   ```bash
   git init
   git add .
   git commit -m "Deploy Ready"
   ```
3. Go to [GitHub](https://github.com/), create a new **Private** or **Public** repository named `college-mail-guardian`.
4. Run the commands shown on GitHub to link and push your repository:
   ```bash
   git branch -M main
   git remote add origin <your-repo-github-link>
   git push -u origin main
   ```

---

## Step 2: Create a Free PostgreSQL Database on Supabase

Render's disk is temporary, meaning SQLite data resets. We will use a free, permanent PostgreSQL database on Supabase instead.

1. Go to [Supabase](https://supabase.com/) and sign up using GitHub.
2. Click **New Project** and create a project. Set a password and select a server region close to you.
3. Once the database is ready, go to **Project Settings** (gear icon) -> **Database**.
4. Scroll down to **Connection string**, select **URI**, and copy the connection string. It looks like:
   `postgresql://postgres.[your-id]:[your-password]@aws-0-us-east-1.pooler.supabase.com:5432/postgres`
5. Replace `[your-password]` in the URI with the actual password you set when creating the project. Save this connection string.

---

## Step 3: Deploy on Render (using Docker)

Our project contains a `Dockerfile` that specifies dependencies and startup commands. Render can build and deploy this container automatically.

1. Go to [Render](https://render.com/) and sign up with GitHub.
2. Click **New +** -> **Web Service**.
3. Select your pushed GitHub repository: `college-mail-guardian`.
4. Configure the service settings:
   - **Name:** `college-mail-guardian`
   - **Environment / Runtime:** Choose **Docker** (Render will automatically read the `Dockerfile` to build and run the app. This is the most stable option!).
   - **Branch:** `main`
   - **Region:** Choose a region close to your database.
5. Scroll down to **Environment Variables** (or click Advanced) and add all variables from your local `.env` file:
   - `GMAIL_CLIENT_ID`
   - `GMAIL_CLIENT_SECRET`
   - `GMAIL_REFRESH_TOKEN`
   - `USER_EMAIL`
   - `GEMINI_API_KEY`
   - `TWILIO_ACCOUNT_SID`
   - `TWILIO_AUTH_TOKEN`
   - `TWILIO_WHATSAPP_NUMBER`
   - `YOUR_WHATSAPP_NUMBER`
   - `SECRET_KEY`
   - **`DATABASE_URL`**: Paste the connection string URI you copied from Supabase in Step 2.
6. Click **Deploy Web Service**. Render will start building the Docker container and start your server. Once successfully deployed, Render will show a live URL (e.g., `https://college-mail-guardian.onrender.com`).

---

## Step 4: Bypass Render Sleep Mode with UptimeRobot (24/7 Active)

To keep your free Render web service awake 24/7 and poll emails continuously:

1. Go to [UptimeRobot](https://uptimerobot.com/) and sign up for a free account.
2. Click **Add New Monitor**.
3. Fill in the monitor settings:
   - **Monitor Type:** `HTTP(s)`
   - **Friendly Name:** `College Mail Guardian`
   - **URL (or IP):** Paste your live Render URL (e.g. `https://college-mail-guardian.onrender.com/`)
   - **Monitoring Interval:** `Every 5 minutes`
4. Click **Create Monitor**.

Now, UptimeRobot will ping your web dashboard page every 5 minutes. This keeps Render awake 24/7, enabling the background worker to continuously poll your inbox and send WhatsApp notifications immediately!
