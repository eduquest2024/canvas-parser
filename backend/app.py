from flask import Flask, request, jsonify, send_file, render_template
from flask_cors import CORS
import os
import uuid
import json
from datetime import datetime
import logging

from canvas import Course, course_to_json, get_courses_list, test_canvas_connection, CourseParsingError

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__, 
            static_folder='../frontend',
            template_folder='../frontend')
CORS(app)  # Enable CORS for frontend communication

# Create directories for file storage
DOWNLOAD_DIR = os.path.join(os.path.dirname(__file__), 'downloads')
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

# Store session data (in production, use proper session management)
sessions = {}

@app.route('/')
def index():
    """Serve the main page"""
    return render_template('index.html')

@app.route('/api/test-connection', methods=['POST'])
def test_connection():
    """Test Canvas API connection"""
    try:
        data = request.get_json()
        api_url = data.get('api_url', '').strip()
        api_key = data.get('api_key', '').strip()
        
        if not api_url or not api_key:
            return jsonify({
                'success': False,
                'message': 'API URL and API Key are required'
            }), 400
        
        # Test connection
        success, message = test_canvas_connection(api_url, api_key)
        
        if success:
            # Store credentials in session (use proper session management in production)
            session_id = str(uuid.uuid4())
            sessions[session_id] = {
                'api_url': api_url,
                'api_key': api_key,
                'created_at': datetime.now()
            }
            
            return jsonify({
                'success': True,
                'message': message,
                'session_id': session_id
            })
        else:
            return jsonify({
                'success': False,
                'message': message
            }), 401
            
    except Exception as e:
        logger.error(f"Error testing connection: {e}")
        return jsonify({
            'success': False,
            'message': f'Connection test failed: {str(e)}'
        }), 500

@app.route('/api/courses', methods=['GET'])
def get_courses():
    """Get list of courses for the authenticated user"""
    try:
        session_id = request.headers.get('Session-Id')
        if not session_id or session_id not in sessions:
            return jsonify({
                'success': False,
                'message': 'Invalid session. Please authenticate first.'
            }), 401
        
        session_data = sessions[session_id]
        api_url = session_data['api_url']
        api_key = session_data['api_key']
        
        courses = get_courses_list(api_url, api_key)
        
        return jsonify({
            'success': True,
            'courses': courses
        })
        
    except CourseParsingError as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 400
    except Exception as e:
        logger.error(f"Error getting courses: {e}")
        return jsonify({
            'success': False,
            'message': f'Failed to get courses: {str(e)}'
        }), 500

@app.route('/api/parse-course', methods=['POST'])
def parse_course():
    """Parse a selected course and generate JSON file"""
    try:
        session_id = request.headers.get('Session-Id')
        if not session_id or session_id not in sessions:
            return jsonify({
                'success': False,
                'message': 'Invalid session. Please authenticate first.'
            }), 401
        
        data = request.get_json()
        course_id = data.get('course_id')
        
        if not course_id:
            return jsonify({
                'success': False,
                'message': 'Course ID is required'
            }), 400
        
        session_data = sessions[session_id]
        api_url = session_data['api_url']
        api_key = session_data['api_key']
        
        # Parse the course
        logger.info(f"Starting to parse course {course_id}")
        course = Course(course_id, api_url, api_key)
        
        # Convert to JSON
        course_json = course_to_json(course)
        
        # Generate filename
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        course_name = course.course.name.replace(' ', '_').replace('/', '_')
        filename = f"course_{course_name}_{timestamp}.json"
        file_path = os.path.join(DOWNLOAD_DIR, filename)
        
        # Save JSON file
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(course_json)
        
        logger.info(f"Course parsing completed. File saved: {filename}")
        
        return jsonify({
            'success': True,
            'message': 'Course parsed successfully',
            'filename': filename,
            'download_url': f'/api/download/{filename}',
            'course_name': course.course.name,
            'modules_count': len(course.modules),
            'total_items': sum(len(module.items) for module in course.modules)
        })
        
    except CourseParsingError as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 400
    except Exception as e:
        logger.error(f"Error parsing course: {e}")
        return jsonify({
            'success': False,
            'message': f'Failed to parse course: {str(e)}'
        }), 500

@app.route('/api/download/<filename>')
def download_file(filename):
    """Download generated JSON file"""
    try:
        file_path = os.path.join(DOWNLOAD_DIR, filename)
        
        if not os.path.exists(file_path):
            return jsonify({
                'success': False,
                'message': 'File not found'
            }), 404
        
        return send_file(
            file_path,
            as_attachment=True,
            download_name=filename,
            mimetype='application/json'
        )
        
    except Exception as e:
        logger.error(f"Error downloading file: {e}")
        return jsonify({
            'success': False,
            'message': f'Download failed: {str(e)}'
        }), 500

@app.route('/api/cleanup', methods=['POST'])
def cleanup_session():
    """Clean up session data"""
    try:
        session_id = request.headers.get('Session-Id')
        if session_id and session_id in sessions:
            del sessions[session_id]
        
        return jsonify({
            'success': True,
            'message': 'Session cleaned up'
        })
        
    except Exception as e:
        logger.error(f"Error cleaning up session: {e}")
        return jsonify({
            'success': False,
            'message': f'Cleanup failed: {str(e)}'
        }), 500

@app.errorhandler(404)
def not_found(error):
    return jsonify({
        'success': False,
        'message': 'Endpoint not found'
    }), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({
        'success': False,
        'message': 'Internal server error'
    }), 500


if __name__ == '__main__':
    # Clean up old files on startup
    try:
        for filename in os.listdir(DOWNLOAD_DIR):
            file_path = os.path.join(DOWNLOAD_DIR, filename)
            if os.path.isfile(file_path):
                # Remove files older than 1 hour
                file_age = datetime.now() - datetime.fromtimestamp(os.path.getctime(file_path))
                if file_age.total_seconds() > 3600:  # 1 hour
                    os.remove(file_path)
                    logger.info(f"Cleaned up old file: {filename}")
    except Exception as e:
        logger.warning(f"Error during startup cleanup: {e}")
    
    # Production-ready server configuration
    port = int(os.environ.get('PORT', 5000))
    debug_mode = os.environ.get('DEBUG', 'False').lower() == 'true'
    app.run(debug=debug_mode, host='0.0.0.0', port=port)
