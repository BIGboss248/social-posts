import os
import re
import json
import urllib.request
import urllib.parse
import sys

# Ensure PyMuPDF (fitz) is installed
try:
    import fitz
except ImportError:
    print("PyMuPDF (fitz) not found. Installing it programmatically...")
    import subprocess
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pymupdf"])
        import fitz
        print("PyMuPDF installed successfully!")
    except Exception as e:
        print(f"Error installing PyMuPDF: {e}")
        print("Please run: pip install pymupdf")
        sys.exit(1)

def sanitize_filename(name):
    name = name.lower()
    name = re.sub(r'[^a-z0-9\s_-]', '', name)
    name = re.sub(r'[\s-]+', '_', name)
    return name.strip('_')

def translate_date(date_str):
    if not date_str:
        return ""
    
    months_map = {
        'janvier': 'ژانویه', 'février': 'فوریه', 'mars': 'مارس', 'avril': 'آوریل',
        'mai': 'مه', 'juin': 'ژوئن', 'juillet': 'ژوئیه', 'août': 'اوت',
        'septembre': 'سپتامبر', 'octobre': 'اکتبر', 'novembre': 'نوامبر', 'décembre': 'دسامبر',
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
            persian_digits = str.maketrans('0123456789', '۰۱۲۳۴۵۶۷۸۹')
            translated_parts.append(clean_part.translate(persian_digits))
            
    return " ".join(translated_parts)

def main():
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
    
    for i, cert in enumerate(certs, 1):
        title = cert['title']
        issuer = cert['issuer']
        date_text = cert['dateText']
        id_text = cert['idText']
        href = cert['href']
        image_url = cert['imageUrl']
        
        persian_date = translate_date(date_text)
        print(f"[{i}/{len(certs)}] Processing: {title}")
        
        base_name = sanitize_filename(title)
        local_path = ""
        
        # Check if we already have the image (jpg, jpeg, or png)
        found_existing = False
        for ext in ['.png', '.jpg', '.jpeg']:
            test_path = os.path.join(certs_dir, f"{base_name}{ext}")
            if os.path.exists(test_path):
                # Verify it is a valid image (not 0 bytes)
                if os.path.getsize(test_path) > 1000:
                    local_path = f"certs/{base_name}{ext}"
                    found_existing = True
                    print(f"  Image already exists: {local_path}")
                    break
        
        if not found_existing:
            # Try downloading/converting
            # First, check if it's a Coursera cert (we can download the PDF and convert it)
            if issuer.lower() in ['coursera', 'google', 'ibm', 'deeplearning.ai', 'stanford university'] and id_text:
                pdf_url = f"https://www.coursera.org/api/certificate.v1/pdf/{id_text}"
                temp_pdf_path = os.path.join(certs_dir, f"temp_{id_text}.pdf")
                png_filename = f"{base_name}.png"
                png_path = os.path.join(certs_dir, png_filename)
                
                try:
                    print(f"  Downloading Coursera PDF: {pdf_url}")
                    req = urllib.request.Request(pdf_url, headers=headers)
                    with urllib.request.urlopen(req, timeout=20) as response:
                        pdf_data = response.read()
                        with open(temp_pdf_path, 'wb') as pdf_file:
                            pdf_file.write(pdf_data)
                    
                    print(f"  Converting PDF to PNG...")
                    doc = fitz.open(temp_pdf_path)
                    page = doc.load_page(0)
                    # Use a higher matrix scale for high resolution (e.g. 2.0 -> 150-200 DPI)
                    zoom = 2.0
                    mat = fitz.Matrix(zoom, zoom)
                    pix = page.get_pixmap(matrix=mat)
                    pix.save(png_path)
                    doc.close()
                    
                    # Clean up temporary PDF
                    if os.path.exists(temp_pdf_path):
                        os.remove(temp_pdf_path)
                        
                    print(f"  Saved converted certificate image to: {png_path}")
                    local_path = f"certs/{png_filename}"
                    found_existing = True
                except Exception as e:
                    print(f"  Failed Coursera PDF flow: {e}")
                    if os.path.exists(temp_pdf_path):
                        try: os.remove(temp_pdf_path)
                        except: pass
            
            # If not a Coursera cert or PDF flow failed, try direct imageUrl download
            if not found_existing and image_url:
                ext = '.jpeg'
                if 'png' in image_url:
                    ext = '.png'
                elif 'gif' in image_url:
                    ext = '.gif'
                elif 'svg' in image_url:
                    ext = '.svg'
                
                local_filename = f"{base_name}{ext}"
                target_path = os.path.join(certs_dir, local_filename)
                
                try:
                    print(f"  Downloading direct image: {image_url}")
                    req = urllib.request.Request(image_url, headers=headers)
                    with urllib.request.urlopen(req, timeout=15) as response:
                        img_data = response.read()
                        with open(target_path, 'wb') as img_file:
                            img_file.write(img_data)
                    print(f"  Saved direct image to: {target_path}")
                    local_path = f"certs/{local_filename}"
                    found_existing = True
                except Exception as e:
                    print(f"  Error downloading direct image: {e}")

        # Update cert dictionary in memory for HTML generation
        href_attr = f'href="{href}" target="_blank"' if href and href != '#' else 'href="#"'
        card_html = f'''                        <a {href_attr} class="cert-compact-card">
                            <span class="cert-compact-title">{title}</span>
                            <span class="cert-compact-meta">
                                <span>{issuer}</span>
                                <span>{persian_date}</span>
                            </span>
                        </a>'''
        grid_html_parts.append(card_html)
        
        if local_path:
            page_html = f'''        <div class="print-cert-page">
            <img src="{local_path}" alt="{title}">
        </div>'''
            gallery_html_parts.append(page_html)

    # Read current HTML
    with open(html_path, 'r', encoding='utf-8') as f:
        html_content = f.read()
        
    grid_inner = "\n\n".join(grid_html_parts)
    gallery_inner = "\n".join(gallery_html_parts)
    
    # Replace in HTML
    grid_pattern = re.compile(r'(<div class="cert-compact-grid">).*?(</div>\s*</section>)', re.DOTALL)
    if grid_pattern.search(html_content):
        html_content = grid_pattern.sub(f'\\1\n{grid_inner}\n                    \\2', html_content)
        print("Updated certifications grid in HTML.")
    else:
        print("Warning: cert-compact-grid container not found in HTML.")
        
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
    main()
