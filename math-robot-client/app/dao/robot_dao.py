import qi
import numpy as np
import cv2
from config import config

class RobotDAO:
    """Data Access Object for robot operations using NAOqi SDK"""
    
    _session = None
    _connected = False
    
    @staticmethod
    def connect():
        """Establish connection to the robot"""
        try:
            RobotDAO._session = qi.Session()
            RobotDAO._session.connect(f"tcp://{config.ROBOT_IP}:{config.ROBOT_PORT}")
            RobotDAO._connected = True
            print(f"✅ Connected to robot at {config.ROBOT_IP}:{config.ROBOT_PORT}")
            return True
        except RuntimeError as e:
            print(f"❌ Failed to connect to robot: {e}")
            RobotDAO._connected = False
            return False
    
    @staticmethod
    def disconnect():
        """Disconnect from the robot"""
        if RobotDAO._session:
            RobotDAO._session.close()
            RobotDAO._connected = False
            print("🔌 Disconnected from robot")
    
    @staticmethod
    def is_connected():
        """Check if robot is connected"""
        return RobotDAO._connected
    
    @staticmethod
    def capture_image(camera_id=1, resolution=3, colorspace=13):
        """
        Capture image from robot's camera and return as bytes
        
        Args:
            camera_id: 0=Top camera, 1=Bottom camera, 2=Depth camera
            resolution: 0=160x120, 1=320x240, 2=640x480, 3=1280x960
            colorspace: 13=RGB, 17=Depth
            
        Returns:
            Dictionary with image data
        """
        if not RobotDAO._connected:
            return {
                'success': False,
                'error': 'Robot not connected'
            }
        
        try:
            vd = RobotDAO._session.service("ALVideoDevice")
            
            # Subscribe to camera
            subscriber_name = f"math_camera_{camera_id}"
            subscriber_id = vd.subscribeCamera(subscriber_name, camera_id, resolution, colorspace, 30)
            
            # Capture frame
            image_data = vd.getImageRemote(subscriber_id)
            vd.unsubscribe(subscriber_id)
            
            if image_data is None:
                return {
                    'success': False,
                    'error': 'No image received from camera'
                }
            
            width, height = image_data[0], image_data[1]
            image_bytes = image_data[6]
            
            # Convert to numpy array for processing if needed
            if colorspace == 13:  # RGB
                np_image = np.frombuffer(image_bytes, np.uint8).reshape(height, width, 3)
                # Convert BGR to RGB
                np_image = cv2.cvtColor(np_image, cv2.COLOR_BGR2RGB)
            elif colorspace == 17:  # Depth
                np_image = np.frombuffer(image_bytes, np.uint16).reshape(height, width)
            else:
                np_image = None
            
            return {
                'success': True,
                'width': width,
                'height': height,
                'image_bytes': image_bytes,
                'numpy_array': np_image,
                'colorspace': colorspace,
                'camera_id': camera_id
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f"Camera capture error: {str(e)}"
            }
    
    @staticmethod
    def say(text, language="English"):
        """Make the robot speak text"""
        if not RobotDAO._connected:
            print(f"🤖 ROBOT SAYS (simulated): {text}")
            return False
        
        try:
            tts = RobotDAO._session.service("ALTextToSpeech")
            tts.say(text, language)
            print(f"🤖 ROBOT SAYS: {text}")
            return True
        except Exception as e:
            print(f"❌ TTS failed: {e}")
            return False
    
    @staticmethod
    def move_to_position(position_name, speed=0.5):
        """Move robot to specific posture"""
        if not RobotDAO._connected:
            print(f"🤖 ROBOT MOVING (simulated): {position_name}")
            return False
        
        try:
            posture_service = RobotDAO._session.service("ALRobotPosture")
            posture_service.goToPosture(position_name, speed)
            print(f"🤖 ROBOT MOVING to: {position_name}")
            return True
        except Exception as e:
            print(f"❌ Movement failed: {e}")
            return False
    
    @staticmethod
    def wake_up():
        """Wake up the robot and stand up"""
        if not RobotDAO._connected:
            print("🤖 ROBOT WAKING UP (simulated)")
            return False
        
        try:
            # Wake up robot
            autonomous_life = RobotDAO._session.service("ALAutonomousLife")
            autonomous_life.setState("solitary")
            
            # Stand up
            return RobotDAO.move_to_position("StandInit", 0.5)
        except Exception as e:
            print(f"❌ Wake up failed: {e}")
            return False
    
    @staticmethod
    def rest():
        """Put robot to rest position"""
        if not RobotDAO._connected:
            print("🤖 ROBOT RESTING (simulated)")
            return False
        
        try:
            return RobotDAO.move_to_position("Crouch", 0.5)
        except Exception as e:
            print(f"❌ Rest failed: {e}")
            return False
    
    @staticmethod
    def get_camera_info():
        """Get information about robot cameras"""
        if not RobotDAO._connected:
            return ["Camera 0: Top (simulated)", "Camera 1: Bottom (simulated)", "Camera 2: Depth (simulated)"]
        
        try:
            vd = RobotDAO._session.service("ALVideoDevice")
            # Get camera info - this is a simplified version
            info = [
                "Camera 0: Top camera",
                "Camera 1: Bottom camera", 
                "Camera 2: Depth camera"
            ]
            return info
        except Exception as e:
            return [f"Error getting camera info: {e}"]