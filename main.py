import os
import io
import base64
import hashlib
import random
from flask import Flask, render_template, request, jsonify
from PIL import Image, ImageDraw, ImageFont
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from collections import defaultdict

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size
app.secret_key = 'your-secret-key-here'

class BloomFilter:
    def __init__(self, size, num_hashes):
        self.size = size
        self.num_hashes = num_hashes
        self.bit_array = [0] * size
        self.added_elements = set()
        self.hash_functions = self._create_hash_functions()
    
    def _create_hash_functions(self):
        """Create multiple hash functions using different salts"""
        salts = ['salt1', 'salt2', 'salt3', 'salt4', 'salt5', 'salt6', 'salt7', 'salt8']
        return [lambda x, salt=salt: int(hashlib.md5((str(x) + salt).encode()).hexdigest(), 16) % self.size 
                for salt in salts[:self.num_hashes]]
    
    def add(self, element):
        """Add an element to the Bloom filter"""
        self.added_elements.add(element)
        for hash_func in self.hash_functions:
            index = hash_func(element)
            self.bit_array[index] = 1
    
    def contains(self, element):
        """Check if an element might be in the Bloom filter"""
        for hash_func in self.hash_functions:
            index = hash_func(element)
            if self.bit_array[index] == 0:
                return False
        return True
    
    def get_hash_positions(self, element):
        """Get the hash positions for an element"""
        positions = []
        for hash_func in self.hash_functions:
            index = hash_func(element)
            positions.append(index)
        return positions
    
    def get_false_positive_rate(self):
        """Calculate theoretical false positive rate"""
        if len(self.added_elements) == 0:
            return 0.0
        
        # Calculate probability of a bit being set
        p = 1 - (1 - 1/self.size) ** (self.num_hashes * len(self.added_elements))
        
        # False positive rate is p^k where k is number of hash functions
        return p ** self.num_hashes

def create_bloom_filter_visualization(bloom_filter, width=800, height=600):
    """Create a visual representation of the Bloom filter with Tinder context"""
    # Create image
    img = Image.new('RGB', (width, height), 'white')
    draw = ImageDraw.Draw(img)
    
    try:
        font_large = ImageFont.truetype("arial.ttf", 20)
        font_medium = ImageFont.truetype("arial.ttf", 16)
        font_small = ImageFont.truetype("arial.ttf", 12)
    except:
        font_large = ImageFont.load_default()
        font_medium = ImageFont.load_default()
        font_small = ImageFont.load_default()
    
    # Calculate bit array visualization
    bit_size = min(20, (width - 100) // bloom_filter.size)
    bit_array_width = bloom_filter.size * bit_size
    start_x = (width - bit_array_width) // 2
    start_y = 100
    
    # Draw title
    draw.text((width//2 - 150, 20), "Tinder Bloom Filter - Swiped Profiles", fill='black', font=font_large)
    
    # Draw bit array
    for i in range(bloom_filter.size):
        x = start_x + i * bit_size
        y = start_y
        
        # Color based on bit value
        color = 'green' if bloom_filter.bit_array[i] == 1 else 'lightgray'
        border_color = 'darkgreen' if bloom_filter.bit_array[i] == 1 else 'gray'
        
        # Draw bit
        draw.rectangle([x, y, x + bit_size - 2, y + bit_size - 2], 
                      fill=color, outline=border_color)
        
        # Draw index
        if i % 10 == 0:  # Show every 10th index
            draw.text((x, y + bit_size + 5), str(i), fill='black', font=font_small)
    
    # Draw statistics
    stats_y = start_y + bit_size + 50
    draw.text((50, stats_y), f"User Pool Size: {bloom_filter.size} profiles", fill='black', font=font_medium)
    draw.text((50, stats_y + 25), f"Hash Functions: {bloom_filter.num_hashes}", fill='black', font=font_medium)
    draw.text((50, stats_y + 50), f"Profiles Swiped: {len(bloom_filter.added_elements)}", fill='black', font=font_medium)
    
    # Calculate and display false positive rate
    fp_rate = bloom_filter.get_false_positive_rate()
    draw.text((50, stats_y + 75), f"False Positive Rate: {fp_rate:.4f}", fill='black', font=font_medium)
    
    # Draw legend
    legend_y = stats_y + 120
    draw.rectangle([50, legend_y, 70, legend_y + 20], fill='green', outline='darkgreen')
    draw.text((80, legend_y), "Profile Swiped (1)", fill='black', font=font_medium)
    draw.rectangle([50, legend_y + 30, 70, legend_y + 50], fill='lightgray', outline='gray')
    draw.text((80, legend_y + 30), "Profile Not Swiped (0)", fill='black', font=font_medium)
    
    return img

def create_hash_visualization(bloom_filter, element, width=800, height=600):
    """Create visualization showing hash positions for a specific profile"""
    img = Image.new('RGB', (width, height), 'white')
    draw = ImageDraw.Draw(img)
    
    try:
        font_large = ImageFont.truetype("arial.ttf", 20)
        font_medium = ImageFont.truetype("arial.ttf", 16)
        font_small = ImageFont.truetype("arial.ttf", 12)
    except:
        font_large = ImageFont.load_default()
        font_medium = ImageFont.load_default()
        font_small = ImageFont.load_default()
    
    # Calculate bit array visualization
    bit_size = min(20, (width - 100) // bloom_filter.size)
    bit_array_width = bloom_filter.size * bit_size
    start_x = (width - bit_array_width) // 2
    start_y = 100
    
    # Draw title
    draw.text((width//2 - 200, 20), f"Checking Profile: '{element}'", fill='black', font=font_large)
    
    # Get hash positions for this element
    hash_positions = bloom_filter.get_hash_positions(element)
    
    # Draw bit array with highlighted positions
    for i in range(bloom_filter.size):
        x = start_x + i * bit_size
        y = start_y
        
        # Determine color
        if i in hash_positions:
            color = 'red'  # Hash position for this profile
            border_color = 'darkred'
        elif bloom_filter.bit_array[i] == 1:
            color = 'green'  # Bit set by other profiles
            border_color = 'darkgreen'
        else:
            color = 'lightgray'  # Bit clear
            border_color = 'gray'
        
        # Draw bit
        draw.rectangle([x, y, x + bit_size - 2, y + bit_size - 2], 
                      fill=color, outline=border_color)
        
        # Draw index
        if i % 10 == 0:
            draw.text((x, y + bit_size + 5), str(i), fill='black', font=font_small)
    
    # Draw hash positions info
    info_y = start_y + bit_size + 50
    draw.text((50, info_y), f"Hash Positions: {hash_positions}", fill='black', font=font_medium)
    
    # Check if element is in filter
    is_in_filter = bloom_filter.contains(element)
    status_color = 'red' if is_in_filter else 'green'
    status_text = "MIGHT BE SWIPED" if is_in_filter else "DEFINITELY NOT SWIPED"
    draw.text((50, info_y + 25), f"Tinder Decision: {status_text}", fill=status_color, font=font_medium)
    
    # Draw legend
    legend_y = info_y + 60
    draw.rectangle([50, legend_y, 70, legend_y + 20], fill='red', outline='darkred')
    draw.text((80, legend_y), f"Hash positions for '{element}'", fill='black', font=font_medium)
    draw.rectangle([50, legend_y + 30, 70, legend_y + 50], fill='green', outline='darkgreen')
    draw.text((80, legend_y + 30), "Profiles already swiped", fill='black', font=font_medium)
    draw.rectangle([50, legend_y + 60, 70, legend_y + 80], fill='lightgray', outline='gray')
    draw.text((80, legend_y + 60), "Profiles not swiped", fill='black', font=font_medium)
    
    return img

def create_comparison_visualization(bloom_filters, width=1200, height=800):
    """Create comparison visualization of multiple Bloom filters"""
    img = Image.new('RGB', (width, height), 'white')
    draw = ImageDraw.Draw(img)
    
    try:
        font_large = ImageFont.truetype("arial.ttf", 20)
        font_medium = ImageFont.truetype("arial.ttf", 16)
        font_small = ImageFont.truetype("arial.ttf", 12)
    except:
        font_large = ImageFont.load_default()
        font_medium = ImageFont.load_default()
        font_small = ImageFont.load_default()
    
    # Draw title
    draw.text((width//2 - 200, 20), "Tinder Bloom Filter Comparison", fill='black', font=font_large)
    
    # Calculate layout
    num_filters = len(bloom_filters)
    cols = min(3, num_filters)
    rows = (num_filters + cols - 1) // cols
    
    filter_width = (width - 50) // cols
    filter_height = (height - 150) // rows
    
    for i, (name, bf) in enumerate(bloom_filters.items()):
        row = i // cols
        col = i % cols
        
        x_offset = 25 + col * filter_width
        y_offset = 80 + row * filter_height
        
        # Draw filter name
        draw.text((x_offset, y_offset), name, fill='black', font=font_medium)
        
        # Calculate bit visualization
        bit_size = min(8, (filter_width - 20) // bf.size)
        bit_array_width = bf.size * bit_size
        start_x = x_offset + (filter_width - bit_array_width) // 2
        start_y = y_offset + 30
        
        # Draw bit array
        for j in range(bf.size):
            x = start_x + j * bit_size
            y = start_y
            
            color = 'green' if bf.bit_array[j] == 1 else 'lightgray'
            border_color = 'darkgreen' if bf.bit_array[j] == 1 else 'gray'
            
            draw.rectangle([x, y, x + bit_size - 1, y + bit_size - 1], 
                          fill=color, outline=border_color)
        
        # Draw statistics
        stats_y = start_y + bit_size + 10
        draw.text((x_offset, stats_y), f"Pool: {bf.size}", fill='black', font=font_small)
        draw.text((x_offset, stats_y + 15), f"Hashes: {bf.num_hashes}", fill='black', font=font_small)
        draw.text((x_offset, stats_y + 30), f"Swiped: {len(bf.added_elements)}", fill='black', font=font_small)
        
        fp_rate = bf.get_false_positive_rate()
        draw.text((x_offset, stats_y + 45), f"FP Rate: {fp_rate:.4f}", fill='black', font=font_small)
    
    return img

def create_performance_analysis(bloom_filters, test_elements, width=800, height=600):
    """Create performance analysis visualization"""
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 8))
    
    # Test each filter
    results = {}
    for name, bf in bloom_filters.items():
        true_positives = 0
        false_positives = 0
        true_negatives = 0
        false_negatives = 0
        
        for element in test_elements:
            is_actually_in = element in bf.added_elements
            is_detected = bf.contains(element)
            
            if is_actually_in and is_detected:
                true_positives += 1
            elif is_actually_in and not is_detected:
                false_negatives += 1
            elif not is_actually_in and is_detected:
                false_positives += 1
            else:
                true_negatives += 1
        
        results[name] = {
            'true_positives': true_positives,
            'false_positives': false_positives,
            'true_negatives': true_negatives,
            'false_negatives': false_negatives
        }
    
    # Plot 1: Accuracy metrics
    names = list(results.keys())
    precision = [results[name]['true_positives'] / (results[name]['true_positives'] + results[name]['false_positives']) 
                 if (results[name]['true_positives'] + results[name]['false_positives']) > 0 else 0 
                 for name in names]
    recall = [results[name]['true_positives'] / (results[name]['true_positives'] + results[name]['false_negatives']) 
              if (results[name]['true_positives'] + results[name]['false_negatives']) > 0 else 0 
              for name in names]
    
    x = np.arange(len(names))
    width = 0.35
    
    ax1.bar(x - width/2, precision, width, label='Precision', color='skyblue')
    ax1.bar(x + width/2, recall, width, label='Recall', color='lightcoral')
    ax1.set_xlabel('Tinder Configuration')
    ax1.set_ylabel('Score')
    ax1.set_title('Tinder Profile Detection Accuracy')
    ax1.set_xticks(x)
    ax1.set_xticklabels(names, rotation=45)
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    
    # Plot 2: False positive rates
    fp_rates = [bf.get_false_positive_rate() for bf in bloom_filters.values()]
    ax2.bar(names, fp_rates, color='orange', alpha=0.7)
    ax2.set_xlabel('Tinder Configuration')
    ax2.set_ylabel('False Positive Rate')
    ax2.set_title('False Positive Rate (Shows Already Swiped Profiles)')
    ax2.tick_params(axis='x', rotation=45)
    ax2.grid(True, alpha=0.3)
    
    plt.tight_layout()
    
    # Convert to PIL Image
    buf = io.BytesIO()
    plt.savefig(buf, format='png', dpi=150, bbox_inches='tight', facecolor='white')
    buf.seek(0)
    plt.close()
    
    return Image.open(buf)

# Global Bloom filter instance
bloom_filter = None

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/create_filter', methods=['POST'])
def create_filter():
    global bloom_filter
    try:
        data = request.get_json()
        size = int(data['size'])
        num_hashes = int(data['num_hashes'])
        
        bloom_filter = BloomFilter(size, num_hashes)
        
        # Create visualization
        vis_image = create_bloom_filter_visualization(bloom_filter)
        
        # Convert to base64
        buffered = io.BytesIO()
        vis_image.save(buffered, format="PNG")
        img_str = base64.b64encode(buffered.getvalue()).decode()
        
        return jsonify({
            'success': True,
            'visualization': img_str,
            'size': size,
            'num_hashes': num_hashes
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/add_element', methods=['POST'])
def add_element():
    global bloom_filter
    try:
        data = request.get_json()
        element = data['element']
        
        if bloom_filter is None:
            return jsonify({'error': 'Bloom filter not created yet'}), 400
        
        bloom_filter.add(element)
        
        # Create visualization
        vis_image = create_bloom_filter_visualization(bloom_filter)
        
        # Convert to base64
        buffered = io.BytesIO()
        vis_image.save(buffered, format="PNG")
        img_str = base64.b64encode(buffered.getvalue()).decode()
        
        return jsonify({
            'success': True,
            'visualization': img_str,
            'element': element,
            'elements_count': len(bloom_filter.added_elements),
            'false_positive_rate': bloom_filter.get_false_positive_rate()
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/check_element', methods=['POST'])
def check_element():
    global bloom_filter
    try:
        data = request.get_json()
        element = data['element']
        
        if bloom_filter is None:
            return jsonify({'error': 'Bloom filter not created yet'}), 400
        
        is_in_filter = bloom_filter.contains(element)
        
        # Create hash visualization
        vis_image = create_hash_visualization(bloom_filter, element)
        
        # Convert to base64
        buffered = io.BytesIO()
        vis_image.save(buffered, format="PNG")
        img_str = base64.b64encode(buffered.getvalue()).decode()
        
        return jsonify({
            'success': True,
            'visualization': img_str,
            'element': element,
            'is_in_filter': is_in_filter,
            'hash_positions': bloom_filter.get_hash_positions(element)
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/add_multiple', methods=['POST'])
def add_multiple():
    global bloom_filter
    try:
        data = request.get_json()
        elements = data['elements'].split(',')
        elements = [elem.strip() for elem in elements if elem.strip()]
        
        if bloom_filter is None:
            return jsonify({'error': 'Bloom filter not created yet'}), 400
        
        for element in elements:
            bloom_filter.add(element)
        
        # Create visualization
        vis_image = create_bloom_filter_visualization(bloom_filter)
        
        # Convert to base64
        buffered = io.BytesIO()
        vis_image.save(buffered, format="PNG")
        img_str = base64.b64encode(buffered.getvalue()).decode()
        
        return jsonify({
            'success': True,
            'visualization': img_str,
            'elements_added': len(elements),
            'total_elements': len(bloom_filter.added_elements),
            'false_positive_rate': bloom_filter.get_false_positive_rate()
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/compare_filters', methods=['POST'])
def compare_filters():
    try:
        data = request.get_json()
        configurations = data['configurations']
        
        # Create multiple Bloom filters
        bloom_filters = {}
        test_elements = ['user_123', 'sarah_456', 'mike_789', 'emma_321', 'john_654', 'lisa_987', 'dave_147', 'anna_258']
        
        for config in configurations:
            name = f"Size:{config['size']}, Hashes:{config['hashes']}"
            bf = BloomFilter(config['size'], config['hashes'])
            
            # Add some test elements
            for element in test_elements[:4]:  # Add first 4 elements
                bf.add(element)
            
            bloom_filters[name] = bf
        
        # Create comparison visualization
        vis_image = create_comparison_visualization(bloom_filters)
        
        # Convert to base64
        buffered = io.BytesIO()
        vis_image.save(buffered, format="PNG")
        img_str = base64.b64encode(buffered.getvalue()).decode()
        
        return jsonify({
            'success': True,
            'visualization': img_str,
            'configurations': len(configurations)
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/performance_analysis', methods=['POST'])
def performance_analysis():
    try:
        data = request.get_json()
        configurations = data['configurations']
        
        # Create multiple Bloom filters
        bloom_filters = {}
        test_elements = ['user_123', 'sarah_456', 'mike_789', 'emma_321', 'john_654', 'lisa_987', 'dave_147', 'anna_258',
                        'tom_369', 'jessica_741', 'alex_852', 'rachel_963', 'chris_159', 'megan_357', 'ryan_753', 'ashley_951']
        
        for config in configurations:
            name = f"Size:{config['size']}, Hashes:{config['hashes']}"
            bf = BloomFilter(config['size'], config['hashes'])
            
            # Add some test elements
            for element in test_elements[:8]:  # Add first 8 elements
                bf.add(element)
            
            bloom_filters[name] = bf
        
        # Create performance analysis
        vis_image = create_performance_analysis(bloom_filters, test_elements)
        
        # Convert to base64
        buffered = io.BytesIO()
        vis_image.save(buffered, format="PNG")
        img_str = base64.b64encode(buffered.getvalue()).decode()
        
        return jsonify({
            'success': True,
            'visualization': img_str
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

def main():
    print("Starting Tinder Bloom Filter Visualizer Flask App...")
    print("Open your browser and navigate to: http://localhost:5000")
    app.run(debug=True, host='0.0.0.0', port=5000)

if __name__ == "__main__":
    main()