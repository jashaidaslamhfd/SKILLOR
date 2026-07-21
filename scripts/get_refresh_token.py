#!/usr/bin/env python3
"""
GET REFRESH TOKEN — Run ONCE locally to get YouTube OAuth refresh token
Run: python scripts/get_refresh_token.py
Then copy the refresh_token to GitHub Secrets
"""
import os
import json
from google_auth_oauthlib.flow import InstalledAppFlow

SCOPES = [
    "https://www.googleapis.com/auth/youtube.upload",
    "https://www.googleapis.com/auth/youtube.force-ssl",
]

def main():
    print("🔐 YOUTUBE OAUTH REFRESH TOKEN GENERATOR")
    print("=" * 50)
    
    client_secrets = "client_secrets.json"
    if not os.path.exists(client_secrets):
        print(f"\n❌ {client_secrets} not found!")
        print("1. Go to Google Cloud Console → APIs & Services → Credentials")
        print("2. Create OAuth 2.0 Client ID (Desktop app)")
        print("3. Download JSON → rename to client_secrets.json → place here")
        return
    
    print(f"\n✅ Found {client_secrets}")
    print("Opening browser for authentication...")
    
    flow = InstalledAppFlow.from_client_secrets_file(client_secrets, SCOPES)
    creds = flow.run_local_server(port=0)
    
    print("\n✅ AUTHENTICATION SUCCESSFUL!")
    print("=" * 50)
    print(f"\n📋 COPY THIS TO GITHUB SECRETS AS 'REFRESH_TOKEN':")
    print(f"\n{creds.refresh_token}")
    print(f"\n📋 ALSO ADD THESE TWO:")
    print(f"GOOGLE_CLIENT_ID: {creds.client_id}")
    print(f"GOOGLE_CLIENT_SECRET: {creds.client_secret}")
    print("\n💾 Save these NOW. You won't see the refresh token again.")
    
    with open("oauth_backup.json", "w") as f:
        json.dump({
            "refresh_token": creds.refresh_token,
            "client_id": creds.client_id,
            "client_secret": creds.client_secret,
        }, f, indent=2)
    print("\n💾 Backed up to oauth_backup.json (keep safe!)")

if __name__ == "__main__":
    main()