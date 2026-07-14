import os
import re
import urllib.request
import urllib.parse
import sys

def sanitize_filename(name):
    # Remove non-ascii and special chars, replace space with underscore
    name = name.lower()
    name = re.sub(r'[^a-z0-9\s_-]', '', name)
    name = re.sub(r'[\s-]+', '_', name)
    return name.strip('_')

def download_certs():
    html_path = 'resume.html'
    certs_dir = 'certs'
    
    if not os.path.exists(html_path):
        print(f"Error: {html_path} not found.")
        return
        
    if not os.path.exists(certs_dir):
        os.makedirs(certs_dir)
        print(f"Created directory: {certs_dir}")
        
    with open(html_path, 'r', encoding='utf-8') as f:
        content = f.read()
        
    # Find the print-cert-gallery block
    gallery_match = re.search(r'<div class="print-cert-gallery">.*?</div>\s*</div>\s*</body>', content, re.DOTALL)
    if not gallery_match:
        # Fallback to general gallery search
        gallery_match = re.search(r'<div class="print-cert-gallery">.*', content, re.DOTALL)
        
    if not gallery_match:
        print("Error: print-cert-gallery container not found in HTML.")
        return
        
    gallery_html = gallery_match.group(0)
    
    # Find all img tags first to support any attribute ordering
    img_tags = re.findall(r'<img\s+[^>]*>', gallery_html, re.IGNORECASE)
    matches = []
    for tag in img_tags:
        src_match = re.search(r'src="([^"]+)"', tag, re.IGNORECASE)
        alt_match = re.search(r'alt="([^"]+)"', tag, re.IGNORECASE)
        if src_match and alt_match:
            matches.append((src_match.group(1), alt_match.group(1)))
            
    print(f"Found {len(matches)} image tags to process.")
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }
    
    updated_content = content
    
    for i, (url, alt) in enumerate(matches, 1):
        print(f"[{i}/{len(matches)}] Processing: {alt}")
        print(f"  URL: {url}")
        
        base_name = sanitize_filename(alt)
        if not base_name:
            base_name = f"cert_{i}"
            
        try:
            req = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(req, timeout=15) as response:
                content_type = response.info().get_content_type()
                ext = '.jpg'
                if 'png' in content_type:
                    ext = '.png'
                elif 'gif' in content_type:
                    ext = '.gif'
                elif 'jpeg' in content_type:
                    ext = '.jpeg'
                elif 'svg' in content_type:
                    ext = '.svg'
                else:
                    # try to infer from url path
                    parsed_url = urllib.parse.urlparse(url)
                    _, url_ext = os.path.splitext(parsed_url.path)
                    if url_ext in ['.jpg', '.jpeg', '.png', '.gif', '.svg', '.webp']:
                        ext = url_ext
                        
                local_filename = f"{base_name}{ext}"
                local_path = os.path.join(certs_dir, local_filename)
                
                # Check for duplicate names and append a suffix if needed
                counter = 1
                while os.path.exists(local_path):
                    local_filename = f"{base_name}_{counter}{ext}"
                    local_path = os.path.join(certs_dir, local_filename)
                    counter += 1
                
                # Download and save the image
                img_data = response.read()
                with open(local_path, 'wb') as img_file:
                    img_file.write(img_data)
                
                print(f"  Saved to: {local_path} ({len(img_data)} bytes)")
                
                # Update HTML string using a safe relative path
                relative_path = f"certs/{local_filename}"
                # Replace exact image tag src
                # We replace exactly the URL that was matched
                updated_content = updated_content.replace(f'src="{url}"', f'src="{relative_path}"')
                
        except Exception as e:
            print(f"  Error downloading image: {e}")
            
    # Write back the updated HTML file
    with open(html_path, 'w', encoding='utf-8') as f:
        f.write(updated_content)
        
    print("\nAll done! HTML file updated with local image paths.")

if __name__ == "__main__":
    download_certs()
