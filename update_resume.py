import os
import re
import json
import urllib.request
import urllib.parse

def sanitize_filename(name):
    name = name.lower()
    name = re.sub(r'[^a-z0-9\s_-]', '', name)
    name = re.sub(r'[\s-]+', '_', name)
    return name.strip('_')

def translate_date(date_str):
    if not date_str:
        return ""
    
    # Translation dictionaries
    months_map = {
        # French
        'janvier': 'ژانویه', 'février': 'فوریه', 'mars': 'مارس', 'avril': 'آوریل',
        'mai': 'مه', 'juin': 'ژوئن', 'juillet': 'ژوئیه', 'août': 'اوت',
        'septembre': 'سپتامبر', 'octobre': 'اکتبر', 'novembre': 'نوامبر', 'décembre': 'دسامبر',
        # English
        'jan': 'ژانویه', 'feb': 'فوریه', 'mar': 'مارس', 'apr': 'آوریل',
        'may': 'مه', 'jun': 'ژوئن', 'jul': 'ژوئیه', 'aug': 'اوت',
        'sep': 'سپتامبر', 'oct': 'اکتبر', 'nov': 'نوامبر', 'dec': 'دسامبر',
        'january': 'ژانویه', 'february': 'فوریه', 'march': 'مارس', 'april': 'آوریل',
        'june': 'ژوئن', 'july': 'ژوئیه', 'august': 'اوت', 'september': 'سپتامبر',
        'october': 'اکتبر', 'november': 'نوامبر', 'december': 'دسامبر'
    }
    
    parts = date_str.lower().split()
    translated_parts = []
    
    for part in parts:
        clean_part = part.strip()
        if clean_part in months_map:
            translated_parts.append(months_map[clean_part])
        else:
            # Map numbers/years (e.g. 2026 -> ۲۰۲۶)
            persian_digits = str.maketrans('0123456789', '۰۱۲۳۴۵۶۷۸۹')
            translated_parts.append(clean_part.translate(persian_digits))
            
    return " ".join(translated_parts)

def update_resume():
    html_path = 'resume.html'
    certs_json_path = 'certs_data.json'
    certs_dir = 'certs'
    
    if not os.path.exists(html_path):
        print(f"Error: {html_path} not found.")
        return
    if not os.path.exists(certs_json_path):
        print(f"Error: {certs_json_path} not found.")
        return
        
    if not os.path.exists(certs_dir):
        os.makedirs(certs_dir)
        
    with open(certs_json_path, 'r', encoding='utf-8') as f:
        certs = json.load(f)
        
    print(f"Loaded {len(certs)} certifications from JSON.")
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }
    
    grid_html_parts = []
    gallery_html_parts = []
    
    # Tracks existing files in certs dir to reuse if possible
    existing_files = os.listdir(certs_dir)
    
    for i, cert in enumerate(certs, 1):
        title = cert['title']
        issuer = cert['issuer']
        date_text = cert['dateText']
        id_text = cert['idText']
        href = cert['href']
        image_url = cert['imageUrl']
        
        # Translate date to Persian
        persian_date = translate_date(date_text)
        
        print(f"[{i}/{len(certs)}] Processing: {title}")
        
        local_path = ""
        base_name = sanitize_filename(title)
        
        if image_url:
            # Determine extension
            ext = '.jpeg'
            if 'png' in image_url:
                ext = '.png'
            elif 'gif' in image_url:
                ext = '.gif'
            elif 'svg' in image_url:
                ext = '.svg'
                
            local_filename = f"{base_name}{ext}"
            target_path = os.path.join(certs_dir, local_filename)
            
            # Check if already exists, else download
            if os.path.exists(target_path):
                print(f"  Image already exists: {target_path}")
                local_path = f"certs/{local_filename}"
            else:
                try:
                    print(f"  Downloading: {image_url}")
                    req = urllib.request.Request(image_url, headers=headers)
                    with urllib.request.urlopen(req, timeout=15) as response:
                        img_data = response.read()
                        with open(target_path, 'wb') as img_file:
                            img_file.write(img_data)
                        print(f"  Saved to: {target_path} ({len(img_data)} bytes)")
                        local_path = f"certs/{local_filename}"
                except Exception as e:
                    print(f"  Error downloading: {e}")
                    
        # Generate grid card HTML
        href_attr = f'href="{href}" target="_blank"' if href and href != '#' else 'href="#"'
        card_html = f'''                        <a {href_attr} class="cert-compact-card">
                            <span class="cert-compact-title">{title}</span>
                            <span class="cert-compact-meta">
                                <span>{issuer}</span>
                                <span>{persian_date}</span>
                            </span>
                        </a>'''
        grid_html_parts.append(card_html)
        
        # Generate print gallery page HTML if we have a local image
        if local_path:
            page_html = f'''        <div class="print-cert-page">
            <img src="{local_path}" alt="{title}">
        </div>'''
            gallery_html_parts.append(page_html)

    # Read current HTML
    with open(html_path, 'r', encoding='utf-8') as f:
        html_content = f.read()
        
    # Construct new grid inner HTML
    grid_inner = "\n\n".join(grid_html_parts)
    
    # Construct new gallery inner HTML
    gallery_inner = "\n".join(gallery_html_parts)
    
    # Replace in HTML
    # Find cert-compact-grid container
    grid_pattern = re.compile(r'(<div class="cert-compact-grid">).*?(</div>\s*</section>)', re.DOTALL)
    if grid_pattern.search(html_content):
        html_content = grid_pattern.sub(f'\\1\n{grid_inner}\n                    \\2', html_content)
        print("Updated certifications grid in HTML.")
    else:
        print("Warning: cert-compact-grid container not found in HTML.")
        
    # Find print-cert-gallery container
    gallery_pattern = re.compile(r'(<div class="print-cert-gallery">).*?(</div>\s*</body>)', re.DOTALL)
    if gallery_pattern.search(html_content):
        html_content = gallery_pattern.sub(f'\\1\n{gallery_inner}\n    \\2', html_content)
        print("Updated certifications print gallery in HTML.")
    else:
        print("Warning: print-cert-gallery container not found in HTML.")
        
    # Save updated HTML
    with open(html_path, 'w', encoding='utf-8') as f:
        f.write(html_content)
        
    print("HTML file updated successfully!")

if __name__ == "__main__":
    update_resume()
