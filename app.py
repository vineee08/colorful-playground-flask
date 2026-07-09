from flask import Flask, render_template, request, jsonify
import random
import datetime
import json

app = Flask(__name__)

# Store user-created palettes (in memory - resets on server restart)
user_palettes = []

# Pre-made palettes
COLOR_PALETTES = [
    {
        'name': 'Sunset Dreams',
        'colors': ['#FF6B6B', '#FF9F43', '#FECA57', '#48DBFB', '#0ABDE3']
    },
    {
        'name': 'Mystic Forest',
        'colors': ['#2C3A47', '#3B5E3B', '#6B8E6B', '#A3C4A3', '#D4E8D4']
    },
    {
        'name': 'Ocean Waves',
        'colors': ['#006994', '#2196F3', '#4FC3F7', '#81D4FA', '#B3E5FC']
    },
    {
        'name': 'Neon Glow',
        'colors': ['#FF00FF', '#00FFFF', '#FF1493', '#00FF00', '#FFD700']
    },
    {
        'name': 'Midnight Galaxy',
        'colors': ['#0A0A2E', '#1A1A4E', '#2D2D6E', '#4A4A8E', '#6A6AAE']
    }
]

@app.route('/')
def home():
    return render_template('index.html', 
                         palettes=COLOR_PALETTES,
                         user_palettes=user_palettes,
                         year=datetime.datetime.now().year)

@app.route('/api/random_color')
def random_color():
    """Generate a random hex color"""
    color = '#' + ''.join(random.choices('0123456789ABCDEF', k=6))
    return jsonify({'color': color})

@app.route('/api/mix_colors', methods=['POST'])
def mix_colors():
    """Mix two colors and return the result"""
    data = request.json
    color1 = data.get('color1', '#FF0000')
    color2 = data.get('color2', '#0000FF')
    
    # Convert hex to RGB
    r1, g1, b1 = hex_to_rgb(color1)
    r2, g2, b2 = hex_to_rgb(color2)
    
    # Average the colors
    r = (r1 + r2) // 2
    g = (g1 + g2) // 2
    b = (b1 + b2) // 2
    
    mixed = rgb_to_hex(r, g, b)
    
    # Get color name (simple approximation)
    color_name = get_color_name(r, g, b)
    
    return jsonify({
        'mixed': mixed,
        'name': color_name,
        'rgb': f'rgb({r}, {g}, {b})'
    })

@app.route('/api/save_palette', methods=['POST'])
def save_palette():
    """Save a user-created palette"""
    data = request.json
    name = data.get('name', 'My Palette')
    colors = data.get('colors', [])
    
    if len(colors) >= 3:
        palette = {
            'name': name,
            'colors': colors,
            'created': datetime.datetime.now().strftime('%Y-%m-%d %H:%M')
        }
        user_palettes.append(palette)
        return jsonify({'success': True, 'palette': palette})
    return jsonify({'success': False, 'error': 'Need at least 3 colors'})

@app.route('/api/complementary/<color>')
def complementary(color):
    """Get complementary color"""
    r, g, b = hex_to_rgb(color)
    # Complementary: (255-r, 255-g, 255-b)
    comp = rgb_to_hex(255-r, 255-g, 255-b)
    return jsonify({'complementary': comp})

@app.route('/api/color_info/<color>')
def color_info(color):
    """Get information about a color"""
    r, g, b = hex_to_rgb(color)
    brightness = (r * 299 + g * 587 + b * 114) / 1000
    color_name = get_color_name(r, g, b)
    
    return jsonify({
        'hex': color,
        'rgb': f'rgb({r}, {g}, {b})',
        'brightness': round(brightness, 2),
        'name': color_name,
        'is_light': brightness > 128
    })

def hex_to_rgb(hex_color):
    """Convert hex to RGB tuple"""
    hex_color = hex_color.lstrip('#')
    return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))

def rgb_to_hex(r, g, b):
    """Convert RGB to hex"""
    return f'#{r:02x}{g:02x}{b:02x}'

def get_color_name(r, g, b):
    """Get a simple color name based on RGB values"""
    # Simple color naming
    max_val = max(r, g, b)
    min_val = min(r, g, b)
    
    if max_val - min_val < 20:
        if r < 30:
            return 'Black'
        elif r > 220:
            return 'White'
        return 'Gray'
    
    if r > g and r > b:
        return 'Red' if r > 200 else 'Pink' if r > 150 else 'Rose'
    elif g > r and g > b:
        return 'Green' if g > 200 else 'Mint'
    elif b > r and b > g:
        return 'Blue' if b > 200 else 'Sky Blue'
    elif r > 150 and g > 150:
        return 'Yellow'
    elif r > 150 and b > 150:
        return 'Purple' if r > b else 'Pink'
    elif g > 150 and b > 150:
        return 'Teal'
    else:
        return 'Colorful'

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)