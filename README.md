# 💕 Tinder Bloom Filter Visualizer

An interactive Flask web application that demonstrates how Tinder uses Bloom filters to efficiently track which profiles you've already swiped on, preventing duplicate matches and improving performance.

## 🌟 Features

- **Tinder-Themed Interface**: Beautiful red gradient design matching Tinder's branding
- **Interactive Swiping Simulation**: Add profiles you've swiped on and see how the Bloom filter tracks them
- **Real-Time Visualization**: See the Bloom filter's bit array update as you swipe
- **Profile Checking**: Check if you've already swiped on a specific profile
- **Performance Analysis**: Compare different Bloom filter configurations
- **Educational Context**: Learn how Tinder uses this data structure in practice

## 🎯 How Tinder Uses Bloom Filters

### **The Problem**
Tinder needs to quickly check if you've already swiped on a profile without storing every single swipe in memory. With millions of users and profiles, this becomes a massive storage and performance challenge.

### **The Solution**
Bloom filters provide a space-efficient way to track swiped profiles:
- **Memory Efficient**: Much smaller than storing all profile IDs
- **Fast Lookups**: O(k) where k = number of hash functions
- **No False Negatives**: If it says "not swiped", it's definitely not there
- **Tolerates False Positives**: Sometimes says "might be swiped" when it's not

### **Tinder's Decision Logic**
- **"DEFINITELY NOT SWIPED"** → Show this profile to the user
- **"MIGHT BE SWIPED"** → Check the database to be sure (rare case)

## 🚀 Installation

### **Prerequisites**
- Python 3.13 or higher
- [uv](https://github.com/astral-sh/uv) package manager

### **Setup**
1. **Clone or download the project**

2. **Install dependencies using uv**:
   ```bash
   uv sync
   ```

3. **Run the application**:
   ```bash
   uv run python main.py
   ```

4. **Open your browser** and navigate to `http://localhost:5000`

##  How to Use

### **Step 1: Create Your Tinder Bloom Filter**
1. **Configure Parameters**:
   - **User Pool Size**: How many profiles the filter can track (50-1000)
   - **Hash Functions**: Number of hash functions (2-6)
   - Click **"Create Tinder Filter"**

2. **What You'll See**:
   - A visual representation of your empty Bloom filter
   - Gray squares represent unswiped profiles
   - Statistics showing your configuration

### **Step 2: Simulate Swiping**
#### **Option A: Swipe on Single Profile**
1. Type a profile ID (e.g., "sarah_456") in the "Profile ID to Like" field
2. Click **"Swipe Right"** or press Enter
3. **What Happens**: 
   - The profile gets hashed by multiple hash functions
   - Corresponding bits in the filter turn green (set to 1)
   - You see the updated false positive rate

#### **Option B: Swipe on Multiple Profiles**
1. Type comma-separated profile IDs (e.g., "user_123, sarah_456, mike_789")
2. Click **"Swipe All"**
3. **What Happens**: All profiles are added simultaneously

### **Step 3: Check Profiles**
1. Type a profile ID to check (e.g., "sarah_456" or "new_user_999")
2. Click **"Check Profile"** or press Enter
3. **What You'll See**:
   - **Red squares**: Hash positions for the checked profile
   - **Green squares**: Bits set by other profiles you've swiped
   - **Status message**: "DEFINITELY NOT SWIPED" or "MIGHT BE SWIPED"

### **Step 4: Advanced Analysis**
#### **Comparison Tab**
1. Click the **"Performance Comparison"** tab
2. Click **"Run Comparison"**
3. **What You'll See**: Side-by-side comparison of different filter configurations

#### **Analysis Tab**
1. Click the **"Analysis"** tab
2. Click **"Run Analysis"**
3. **What You'll See**: Charts showing precision, recall, and false positive rates

## 🧠 Technical Details

### **Bloom Filter Algorithm**
```
When you swipe on "sarah_456":
- "sarah_456" gets hashed by all 3 hash functions
- Hash function 1 → position 23 (sets bit 23 to 1)
- Hash function 2 → position 67 (sets bit 67 to 1)  
- Hash function 3 → position 89 (sets bit 89 to 1)
- These bits turn green in the visualization
```

### **Profile Checking Process**
```
When you check "new_user_999":
- "new_user_999" gets hashed by all 3 hash functions
- Hash function 1 → position 45
- Hash function 2 → position 12
- Hash function 3 → position 78
- If ALL these positions are 1 → "MIGHT BE SWIPED"
- If ANY position is 0 → "DEFINITELY NOT SWIPED"
```

### **False Positives in Tinder Context**
```
Scenario: You swiped on "sarah_456" and "mike_789"
- "sarah_456" sets bits: [23, 67, 89]
- "mike_789" sets bits: [12, 45, 78]
- Now checking "emma_321" (you haven't swiped)
- "emma_321" hashes to: [23, 45, 89]
- Since bits 23, 45, and 89 are all 1 → "MIGHT BE SWIPED"
- This is a FALSE POSITIVE!
- Tinder would double-check the database (rare case)
```

## 🎨 Visual Elements Explained

### **Color Coding**
- **Gray squares**: Unswiped profiles (0s) - no profiles hash to these positions
- **Green squares**: Swiped profiles (1s) - at least one profile hashed to this position
- **Red squares**: Hash positions for the currently checked profile

### **Statistics Display**
- **User Pool Size**: Total number of profiles the filter can track
- **Hash Functions**: Number of hash functions used
- **Profiles Swiped**: How many unique profiles you've swiped on
- **False Positive Rate**: Probability of getting a false positive

### **Status Messages**
- **"DEFINITELY NOT SWIPED"**: At least one hash position is 0
- **"MIGHT BE SWIPED"**: All hash positions are 1 (could be true or false positive)

## 🔧 Configuration Trade-offs

### **User Pool Size**
- **Larger pool** = Lower false positive rate but more memory
- **Smaller pool** = Higher false positive rate but less memory

### **Hash Functions**
- **More hash functions** = Lower false positive rate but slower operations
- **Fewer hash functions** = Higher false positive rate but faster operations

### **Profiles Added**
- **More profiles swiped** = Higher false positive rate
- **Fewer profiles swiped** = Lower false positive rate

## 🌍 Real-World Applications

### **Tinder's Use Cases**
- **Profile Deduplication**: Prevent showing the same profile twice
- **Memory Efficiency**: Handle millions of users without massive storage
- **Fast Matching**: Quick profile checks during swiping

### **Other Applications**
- **Web browsers**: Check if URLs are malicious
- **Databases**: Check if records exist before expensive lookups
- **Spell checkers**: Check if words are in dictionary
- **Network routers**: Check if packets should be blocked

## 🛠️ Development

### **Using uv for development**:
```bash
# Install development dependencies
uv sync --group dev

# Run tests
uv run pytest

# Format code
uv run black .

# Lint code
uv run flake8
```

### **Project Structure**
```
Tinder-Bloom-Filter-Visualizer/
├── main.py              # Flask application with Tinder context
├── __init__.py          # Package initialization
├── templates/
│   └── index.html       # Tinder-themed web interface
├── uploads/             # Temporary upload directory
├── pyproject.toml       # Project configuration and dependencies
└── README.md           # This file
```

## 📊 Performance Metrics

### **Memory Efficiency**
- **Traditional approach**: Store every profile ID (hundreds of MB)
- **Bloom filter approach**: Store bit array (few KB)
- **Space savings**: 99%+ reduction in memory usage

### **Speed Benefits**
- **Lookup time**: O(k) where k = number of hash functions
- **Typical k**: 3-5 hash functions
- **Result**: Sub-millisecond profile checks

### **Accuracy Trade-offs**
- **False positive rate**: Typically 1-5% for well-configured filters
- **False negative rate**: 0% (never misses a swiped profile)
- **Database fallback**: Only needed for false positives (rare)

## 🚨 Troubleshooting

### **Common Issues**
1. **Port already in use**: Change the port in `main.py` or kill the process using the port
2. **Profile check fails**: Check profile ID format and ensure filter is created
3. **Dependencies not found**: Run `uv sync` to install dependencies

### **uv Commands Reference**
```bash
# Install dependencies
uv sync

# Add a new dependency
uv add package-name

# Add development dependency
uv add --group dev package-name

# Run a command in the virtual environment
uv run command

# Activate the virtual environment
uv shell

# Update dependencies
uv lock --upgrade
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly with `uv run pytest`
5. Submit a pull request

## 📄 License

This project is open source and available under the MIT License.

##  Acknowledgments

- Built with Flask and Bootstrap 5
- Uses Pillow for image processing
- Package management with uv
- Inspired by Tinder's real-world use of Bloom filters
- Educational tool for understanding probabilistic data structures

---

**💡 Pro Tip**: Start with a small user pool (50-100) and 2-3 hash functions to see the concept clearly, then experiment with larger configurations to understand the trade-offs!