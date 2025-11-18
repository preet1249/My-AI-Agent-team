# 🚨 SECURITY ALERT - CREDENTIALS EXPOSED

## ⚠️ IMMEDIATE ACTION REQUIRED

Your credentials were temporarily exposed in `DEPLOY.md` in git commit history.

**Status**: Credentials have been removed from current files, but they exist in git history.

---

## 🔴 YOU MUST ROTATE THESE CREDENTIALS NOW:

### 1. OpenRouter API Key (CRITICAL)
**What was exposed**: `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`

**How to rotate**:
1. Go to https://openrouter.ai
2. Go to **Keys** section
3. **Delete** the exposed key
4. **Create** new key
5. Update your local `.env` file

### 2. Supabase Service Role Key (CRITICAL)
**What was exposed**: Service role key starting with `eyJhbGci...`

**How to rotate**:
1. Go to https://whdtxycynbxwyaqpxajg.supabase.co
2. Go to **Settings** → **API**
3. Click **Reset** service_role key
4. Copy new key
5. Update your local `.env` file
6. Update Render environment variables

### 3. Upstash Redis Token (CRITICAL)
**What was exposed**: Redis token `AWc1AAI...`

**How to rotate**:
1. Go to https://upstash.com
2. Go to your Redis database
3. Click **Reset** password/token
4. Copy new connection string
5. Update your local `.env` file

### 4. Internal Security Keys (MODERATE)
**What was exposed**:
- INTERNAL_SIGNING_KEY
- WEBHOOK_SECRET

**How to rotate**:
```bash
# Generate new keys
openssl rand -hex 32  # For INTERNAL_SIGNING_KEY
openssl rand -hex 32  # For WEBHOOK_SECRET
```

Update both in your local `.env` file.

---

## ✅ AFTER ROTATING ALL CREDENTIALS:

1. **Update local `.env`**:
   ```bash
   # Edit apps/backend/.env with NEW credentials
   ```

2. **Update Render**:
   - Go to Render dashboard
   - Click your service → **Environment**
   - Update all the new values

3. **Verify .env is not tracked**:
   ```bash
   cd "C:\Users\mt\AI Agents\AI Agent Team"
   git status
   # Should NOT show apps/backend/.env
   ```

4. **Deploy with new credentials**:
   - Render will auto-redeploy when you update environment variables

---

## 🔒 SECURITY MEASURES NOW IN PLACE:

✅ `.env` added to `.gitignore`
✅ Credentials removed from `DEPLOY.md`
✅ All future commits will NOT include `.env`

---

## 📋 CHECKLIST:

- [ ] Rotate OpenRouter API key
- [ ] Reset Supabase service_role key
- [ ] Reset Upstash Redis token
- [ ] Generate new INTERNAL_SIGNING_KEY
- [ ] Generate new WEBHOOK_SECRET
- [ ] Update local `.env` file
- [ ] Update Render environment variables
- [ ] Test backend still works
- [ ] Delete this file after completion

---

## ⏰ DO THIS IMMEDIATELY

The exposed credentials are in public git history. Anyone with access to the repository can see them.

**Estimated time**: 10 minutes to rotate everything.

---

I sincerely apologize for this mistake. I should have been more careful with credential handling.

The system is still secure once you rotate these credentials.
