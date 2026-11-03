import os
import zipfile
import shutil

repo_root = r"C:\Users\user\.gemini\antigravity\scratch\srihanumsastha-catalogue"
desktop_zip = r"C:\Users\user\Desktop\srihanumsastha-catalogue.zip"
downloads_zip = r"C:\Users\user\Downloads\srihanumsastha-catalogue.zip"

excluded_dirs = {'.git', '__pycache__', '.pytest_cache', 'venv', '.env', 'node_modules'}
excluded_files = {'*.pyc'}

temp_zip = os.path.join(repo_root, "bundle_temp.zip")
if os.path.exists(temp_zip):
    os.remove(temp_zip)

print("Creating delivery ZIP archive...")
with zipfile.ZipFile(temp_zip, 'w', zipfile.ZIP_DEFLATED) as zipf:
    for root, dirs, files in os.walk(repo_root):
        dirs[:] = [d for d in dirs if d not in excluded_dirs]
        for file in files:
            if file == "bundle_temp.zip" or file.endswith(".pyc"):
                continue
            full_path = os.path.join(root, file)
            rel_path = os.path.relpath(full_path, repo_root)
            zipf.write(full_path, arcname=rel_path)

size_mb = os.path.getsize(temp_zip) / (1024 * 1024)
print(f"Archive built: {size_mb:.2f} MB")

# Copy to Desktop and Downloads
shutil.copy2(temp_zip, desktop_zip)
shutil.copy2(temp_zip, downloads_zip)
os.remove(temp_zip)

print(f"[SUCCESS] Copied to Desktop: {desktop_zip} ({os.path.getsize(desktop_zip) / (1024 * 1024):.2f} MB)")
print(f"[SUCCESS] Copied to Downloads: {downloads_zip} ({os.path.getsize(downloads_zip) / (1024 * 1024):.2f} MB)")
