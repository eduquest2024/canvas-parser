from canvasapi import Canvas
from bs4 import BeautifulSoup
import json
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class CourseParsingError(Exception):
    """Custom exception for course parsing errors"""
    pass


class Course:
    def __init__(self, course_id, API_URL, API_KEY):
        try:
            self.API_URL = API_URL
            self.API_KEY = API_KEY
            self.canvas = Canvas(API_URL, API_KEY)
            self.course = self.canvas.get_course(course_id)
            self.course_id = course_id
            
            # Get modules with error handling
            try:
                modules = list(self.course.get_modules())
                self.module_ids = [module.id for module in modules]
            except Exception as e:
                logger.warning(f"Error getting modules for course {course_id}: {e}")
                self.module_ids = []
            
            self.modules = []
            for module_id in self.module_ids:
                try:
                    module = self.Module(self, module_id)
                    self.modules.append(module)
                except Exception as e:
                    logger.warning(f"Error processing module {module_id}: {e}")
                    continue
                    
        except Exception as e:
            raise CourseParsingError(f"Failed to initialize course {course_id}: {e}")

    class Module:
        def __init__(self, Course, module_id):
            try:
                self.course = Course.course
                self.module = self.course.get_module(module_id)
                self.course_id = self.course.id
                self.title = self.module.name
                self.items = []
                
                try:
                    module_items = list(self.module.get_module_items())
                    self.item_ids = [item.id for item in module_items]
                except Exception as e:
                    logger.warning(f"Error getting items for module {module_id}: {e}")
                    self.item_ids = []
                
                for item_id in self.item_ids:
                    try:
                        item = self.get_item(item_id)
                        if item is not None:
                            self.items.append(item)
                    except Exception as e:
                        logger.warning(f"Error processing item {item_id}: {e}")
                        continue
                        
            except Exception as e:
                logger.error(f"Failed to initialize module {module_id}: {e}")
                raise

        class Assignment:
            def __init__(self, assignment_id, course):
                try:
                    self.course = course
                    self.cv_assignment = self.course.get_assignment(assignment_id)
                    self.title = self.cv_assignment.name
                    self.description = None
                    if self.cv_assignment.description is not None:
                        try:
                            html_content = self.cv_assignment.description
                            soup = BeautifulSoup(html_content, "html.parser")
                            for tag in soup(["script", "style", "link"]):
                                tag.decompose()
                            self.description = soup.get_text(separator="\n", strip=True)
                        except Exception as e:
                            logger.warning(f"Error parsing assignment description: {e}")
                            self.description = "Error parsing description"
                    
                    try:
                        self.due_date = str(self.cv_assignment.due_at_date)
                    except Exception as e:
                        logger.warning(f"Error getting due date: {e}")
                        self.due_date = "NA"
                        
                except Exception as e:
                    logger.error(f"Failed to initialize assignment {assignment_id}: {e}")
                    raise

        class Quiz:
            def __init__(self, quiz_id, course):
                try:
                    self.course = course
                    self.quiz = self.course.get_quiz(quiz_id)
                    self.title = self.quiz.title
                    self.description = None
                    
                    if self.quiz.description is not None:
                        try:
                            html_content = self.quiz.description
                            soup = BeautifulSoup(html_content, "html.parser")
                            for tag in soup(["script", "style", "link"]):
                                tag.decompose()
                            self.description = soup.get_text(separator="\n", strip=True)
                        except Exception as e:
                            logger.warning(f"Error parsing quiz description: {e}")
                            self.description = "Error parsing description"
                            
                except Exception as e:
                    logger.error(f"Failed to initialize quiz {quiz_id}: {e}")
                    raise

        class File:
            def __init__(self, file_id, course):
                try:
                    self.course = course
                    self.file = self.course.get_file(file_id)
                    self.id = file_id
                    self.title = self.file.display_name
                    self.description = None  # Files don't typically have descriptions
                    
                    try:
                        self.download_url = self.file.url
                    except Exception as e:
                        logger.warning(f"Error getting file URL: {e}")
                        self.download_url = "NA"
                        
                    self.content = None
                    self.processed_content = None
                    self.metadata = {}
                    
                except Exception as e:
                    logger.error(f"Failed to initialize file {file_id}: {e}")
                    raise

        class Page:
            def __init__(self, page_id, course):
                try:
                    self.course = course
                    self.page = self.course.get_page(page_id)
                    self.title = self.page.title
                    self.description = None
                    self.body = None
                    
                    if self.page.body is not None:
                        try:
                            html_content = self.page.body
                            soup = BeautifulSoup(html_content, "html.parser")
                            for tag in soup(["script", "style", "link"]):
                                tag.decompose()
                            self.body = soup.get_text(separator="\n", strip=True)
                            self.description = self.body  # Use body as description for consistency
                        except Exception as e:
                            logger.warning(f"Error parsing page body: {e}")
                            self.description = "Error parsing page content"
                            
                except Exception as e:
                    logger.error(f"Failed to initialize page {page_id}: {e}")
                    raise

        class Discussion:
            def __init__(self, discussion_id, course):
                try:
                    self.course = course
                    self.discussion = self.course.get_discussion_topic(discussion_id)
                    self.title = self.discussion.title
                    self.description = None
                    self.body = None
                    
                    if self.discussion.message is not None:
                        try:
                            html_content = self.discussion.message
                            soup = BeautifulSoup(html_content, "html.parser")
                            for tag in soup(["script", "style", "link"]):
                                tag.decompose()
                            self.body = soup.get_text(separator="\n", strip=True)
                            self.description = self.body  # Use body as description for consistency
                        except Exception as e:
                            logger.warning(f"Error parsing discussion message: {e}")
                            self.description = "Error parsing discussion content"
                            
                except Exception as e:
                    logger.error(f"Failed to initialize discussion {discussion_id}: {e}")
                    raise

        def get_item(self, item_id):
            try:
                item = self.module.get_module_item(item_id)
                
                if item.type == 'Assignment':
                    return self.Assignment(item.content_id, self.course)
                elif item.type == 'Quiz':
                    return self.Quiz(item.content_id, self.course)
                elif item.type == 'File':
                    return self.File(item.content_id, self.course)
                elif item.type == 'Page':
                    return self.Page(item.content_id, self.course)  # Fixed: use content_id instead of title
                elif item.type == 'Discussion':
                    return self.Discussion(item.content_id, self.course)
                else:
                    logger.info(f"Unsupported item type: {item.type}")
                    return None
                    
            except Exception as e:
                logger.error(f"Error getting item {item_id}: {e}")
                return None


def course_to_json(course_obj):
    """Convert a Course object to JSON with error handling"""
    def datetime_handler(obj):
        if hasattr(obj, 'isoformat'):
            return obj.isoformat()
        return 'NA'

    try:
        course_dict = {
            "course_name": getattr(course_obj.course, 'name', 'Unknown Course'),
            "course_id": course_obj.course_id,
            "modules": []
        }

        for module in course_obj.modules:
            try:
                module_dict = {
                    "title": getattr(module, 'title', 'Unknown Module'),
                    "items": []
                }

                for item in module.items:
                    if item is not None:  # Handle None items
                        try:
                            item_dict = {
                                "type": item.__class__.__name__,
                                "title": getattr(item, 'title', 'NA'),
                                "description": getattr(item, 'description', 'NA'),
                                "due_date": datetime_handler(getattr(item, 'due_date', 'NA')),
                                "download_link": getattr(item, 'download_url', 'NA'),
                                "file_type": getattr(item, 'mime_type', 'NA')
                            }
                            module_dict["items"].append(item_dict)
                        except Exception as e:
                            logger.warning(f"Error serializing item: {e}")
                            continue

                course_dict["modules"].append(module_dict)
                
            except Exception as e:
                logger.warning(f"Error processing module: {e}")
                continue

        return json.dumps(course_dict, indent=2)
        
    except Exception as e:
        logger.error(f"Error converting course to JSON: {e}")
        raise CourseParsingError(f"Failed to convert course to JSON: {e}")


def get_courses_list(API_URL, API_KEY):
    """Get list of courses for the authenticated user"""
    try:
        canvas = Canvas(API_URL, API_KEY)
        courses = list(canvas.get_courses())
        
        courses_data = []
        for course in courses:
            try:
                course_info = {
                    "id": course.id,
                    "name": course.name,
                    "code": getattr(course, 'course_code', 'N/A'),
                    "workflow_state": getattr(course, 'workflow_state', 'unknown')
                }
                courses_data.append(course_info)
            except Exception as e:
                logger.warning(f"Error processing course: {e}")
                continue
                
        return courses_data
        
    except Exception as e:
        logger.error(f"Error getting courses list: {e}")
        raise CourseParsingError(f"Failed to get courses: {e}")


def test_canvas_connection(API_URL, API_KEY):
    """Test Canvas API connection"""
    try:
        canvas = Canvas(API_URL, API_KEY)
        # Try to get user info to test connection
        user = canvas.get_current_user()
        return True, f"Connected as {user.name}"
    except Exception as e:
        return False, f"Connection failed: {e}"