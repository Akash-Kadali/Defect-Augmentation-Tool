import os, sys, logging, random, json, base64, webbrowser, zipfile
from flask import Flask, render_template, request, jsonify, send_from_directory, send_file
from dotenv import load_dotenv
from jinja2 import FileSystemLoader, ChoiceLoader
from tempfile import NamedTemporaryFile
from PIL import Image
from io import BytesIO
import re
import fnmatch

load_dotenv()
PORT = int(os.getenv("PORT", 5000))
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(BASE_DIR, '..'))

PERFECT_DIR = os.path.join(PROJECT_ROOT, 'Laser_Perfect_Colored')
DEFECTS_DIR = os.path.join(PROJECT_ROOT, 'Laser_Defects_Colored')
ORIGINAL_DEFECTS_DIR = os.path.join(PROJECT_ROOT, 'Laser Defects')
OUTPUTS_DIR = os.path.join(PROJECT_ROOT, 'outputs')
PLACED_DIR = os.path.join(OUTPUTS_DIR, 'Placed_Defects')
STATIC_DIR = os.path.join(PROJECT_ROOT, 'frontend', 'static')
TEMPLATES_DIR = os.path.join(PROJECT_ROOT, 'frontend', 'templates')
SESSION_FILE = os.path.join(OUTPUTS_DIR, 'session_state.json')

os.makedirs(PLACED_DIR, exist_ok=True)
app = Flask(__name__, static_folder=STATIC_DIR, template_folder=TEMPLATES_DIR)

if getattr(sys, 'frozen', False):
    app.jinja_loader = ChoiceLoader([
        FileSystemLoader(os.path.join(sys._MEIPASS, 'frontend', 'templates')),
        app.jinja_loader
    ])

logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(message)s')

def load_session():
    if os.path.exists(SESSION_FILE):
        with open(SESSION_FILE, 'r') as f:
            return json.load(f)
    return {
        'color': None,
        'defect_name': None,
        'defect_index': 0,
        'defect_list': [],
        'used_images': [],
        'save_count': 0
    }

def save_session():
    with open(SESSION_FILE, 'w') as f:
        json.dump(defect_state, f)

defect_state = load_session()
def get_color_folders():
    return sorted(os.listdir(DEFECTS_DIR))

def get_defect_list(color):
    folder = os.path.join(DEFECTS_DIR, color)
    return sorted([f for f in os.listdir(folder) if f.endswith('.png')])

def get_random_perfect_image(color, used, defect_name):
    folder = os.path.join(PERFECT_DIR, color)
    all_images = [f for f in os.listdir(folder) if f.endswith(('.jpg', '.png'))]

    # Extract ID prefix like P10924 from defect name
    base_id = defect_name.split('_die_')[0]

    # Match any perfect image that starts with same ID
    candidates = [f for f in all_images if f.startswith(base_id + '_die_')]

    return random.choice(candidates) if candidates else None

@app.route('/')
def index():
    return render_template('index.html', colors=get_color_folders())

@app.route('/init/<color>')
def init_color(color):
    defect_list = get_defect_list(color)
    if not defect_list:
        return jsonify({'status': 'error', 'message': 'No defects found for this color'})

    defect_state.update({
        'color': color,
        'defect_index': 0,
        'defect_list': defect_list,
        'defect_name': defect_list[0],
        'used_images': [],
        'save_count': 0
    })
    save_session()
    return jsonify({'status': 'success', 'defect': defect_state['defect_name']})
def extract_base_image_name(filename):
    return re.sub(r'_defect(_\d+)?\.png$', '', filename)

def get_progress(color):
    defect_folder = os.path.join(DEFECTS_DIR, color)
    placed_folder = os.path.join(PLACED_DIR, color)
    os.makedirs(placed_folder, exist_ok=True)

    defect_filenames = [f for f in os.listdir(defect_folder) if f.endswith('.png')]
    total_defects = len(defect_filenames)
    completed = 0

    for defect_file in defect_filenames:
        base = defect_file.replace('.png', '')
        expected = [f"{base}_augment_{i}.jpg" for i in range(1, 46)]
        if all(os.path.exists(os.path.join(placed_folder, fname)) for fname in expected):
            completed += 1

    return completed, total_defects

@app.route('/progress/<color>')
def get_progress_info(color):
    current, total = get_progress(color)
    return jsonify({'current': current, 'total': total})


@app.route('/next')
def get_next_image():
    color = defect_state['color']
    perfect_name = get_random_perfect_image(color, defect_state['used_images'], defect_state['defect_name'])

    if not perfect_name:
        return jsonify({'status': 'error', 'message': 'No more perfect images'}), 400

    defect_state['used_images'].append(perfect_name)
    defect_state['save_count'] += 1
    save_session()

    defect_name = defect_state['defect_name']
    base_name = extract_base_image_name(defect_name)

    # ✅ Corrected paths (no color folder inside Laser Defects)
    jpg_path = os.path.join(ORIGINAL_DEFECTS_DIR, base_name + '.jpg')
    png_path = os.path.join(ORIGINAL_DEFECTS_DIR, base_name + '.png')

    if os.path.exists(jpg_path):
        original_name = base_name + '.jpg'
    elif os.path.exists(png_path):
        original_name = base_name + '.png'
    else:
        original_name = None

    defect_base = defect_name.replace('.png', '')
    expected = [f"{defect_base}_augment_{i}.jpg" for i in range(1, 46)]
    folder = os.path.join(PLACED_DIR, color)
    done = all(os.path.exists(os.path.join(folder, fname)) for fname in expected)


    return jsonify({
        'status': 'ok',
        'defect_image': os.path.join('Laser_Defects_Colored', color, defect_name),
        'perfect_image': os.path.join('Laser_Perfect_Colored', color, perfect_name),
        'original_image': os.path.join('Laser Defects', original_name) if original_name else '',
        'defect_name': defect_name,
        'perfect_name': perfect_name,
        'count': defect_state['save_count'],
        'done': done
    })


def get_defect_save_count(color, defect_name):
    base_name = extract_base_image_name(defect_name)
    folder = os.path.join(PLACED_DIR, color)
    if not os.path.exists(folder):
        return 0
    matching = [f for f in os.listdir(folder) if f.startswith(base_name + '_augment_') and f.endswith('.jpg')]
    return len(matching)



@app.route('/save', methods=['POST'])
def save_composite():
    data = request.get_json()
    image_data = data.get('composite')
    filename = data.get('filename')

    if not image_data or not filename:
        return jsonify({'status': 'error', 'message': 'Missing data'}), 400

    img = Image.open(BytesIO(base64.b64decode(image_data.split(',')[1]))).convert('RGB')
    save_path = os.path.join(PLACED_DIR, defect_state['color'])
    os.makedirs(save_path, exist_ok=True)
    img.save(os.path.join(save_path, filename))

    # Return updated progress too
    current, total = get_progress(defect_state['color'])
    return jsonify({'status': 'success', 'saved': filename, 'current': current, 'total': total})

@app.route('/skip/<direction>')
def skip_defect(direction):
    if direction == 'next':
        defect_state['defect_index'] = min(defect_state['defect_index'] + 1, len(defect_state['defect_list']) - 1)
    elif direction == 'prev':
        defect_state['defect_index'] = max(defect_state['defect_index'] - 1, 0)
    defect_state['defect_name'] = defect_state['defect_list'][defect_state['defect_index']]
    defect_state['save_count'] = 0
    save_session()
    return jsonify({'status': 'ok', 'defect': defect_state['defect_name']})

@app.route('/reset_session', methods=['POST'])
def reset_session():
    global defect_state
    defect_state = {
        'color': None,
        'defect_name': None,
        'defect_index': 0,
        'defect_list': [],
        'used_images': [],
        'save_count': 0
    }
    save_session()
    return jsonify({'status': 'reset'})

@app.route('/refresh_background')
def refresh_background():
    color = defect_state['color']
    defect_name = defect_state['defect_name']

    perfect_name = get_random_perfect_image(color, defect_state['used_images'], defect_name)
    if not perfect_name:
        return jsonify({'status': 'error', 'message': 'No more perfect images'})

    defect_state['used_images'].append(perfect_name)
    save_session()

    base_name = extract_base_image_name(defect_name)
    jpg_path = os.path.join(ORIGINAL_DEFECTS_DIR, base_name + '.jpg')
    png_path = os.path.join(ORIGINAL_DEFECTS_DIR, base_name + '.png')
    original_name = base_name + '.jpg' if os.path.exists(jpg_path) else base_name + '.png' if os.path.exists(png_path) else None

    defect_base = defect_name.replace('.png', '')
    expected = [f"{defect_base}_augment_{i}.jpg" for i in range(1, 46)]
    folder = os.path.join(PLACED_DIR, color)
    done = all(os.path.exists(os.path.join(folder, fname)) for fname in expected)


    return jsonify({
        'status': 'ok',
        'defect_image': os.path.join('Laser_Defects_Colored', color, defect_name),
        'perfect_image': os.path.join('Laser_Perfect_Colored', color, perfect_name),
        'original_image': os.path.join('Laser Defects', original_name) if original_name else '',
        'defect_name': defect_name,
        'perfect_name': perfect_name,
        'count': defect_state['save_count'],
        'done': done
    })



@app.route('/download/<color>')
def download_zip(color):
    folder = os.path.join(PLACED_DIR, color)
    zipname = f"defects_{color}.zip"
    with NamedTemporaryFile(delete=False) as tmp:
        with zipfile.ZipFile(tmp.name, 'w') as z:
            for f in os.listdir(folder):
                z.write(os.path.join(folder, f), arcname=f)
        tmp.flush()
        return send_file(tmp.name, download_name=zipname, as_attachment=True)
@app.route('/Laser_Perfect_Colored/<color>/<filename>')
def serve_perfect(color, filename):
    return send_from_directory(os.path.join(PERFECT_DIR, color), filename)

@app.route('/Laser_Defects_Colored/<color>/<filename>')
def serve_defect(color, filename):
    return send_from_directory(os.path.join(DEFECTS_DIR, color), filename)

@app.route('/Laser Defects/<filename>')
def serve_original_defect(filename):
    return send_from_directory(ORIGINAL_DEFECTS_DIR, filename)

def open_browser():
    if os.environ.get("WERKZEUG_RUN_MAIN") != "true":
        webbrowser.open(f"http://127.0.0.1:{PORT}")

if __name__ == '__main__':
    open_browser()
    app.run(host='0.0.0.0', port=PORT, debug=True)
