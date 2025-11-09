import time
from app.dao.api_dao import ApiDAO
from app.dao.wolfram_dao import WolframDAO
from app.dao.robot_dao import RobotDAO

class PipelineService:
    """Service orchestrating the complete mathematical processing pipeline"""
    
    @staticmethod
    def run_complete_pipeline():
        """Execute complete pipeline: robot setup → capture → API → Wolfram → results"""
        print("🚀 Starting Math Robot Client Pipeline...")
        start_time = time.time()
        
        try:
            # Step 1: Connect to robot and setup
            print("🔗 Step 1: Connecting to robot...")
            if not RobotDAO.connect():
                print("❌ Robot connection failed, running in simulation mode")
            
            # Step 2: Wake up robot and prepare
            print("🤖 Step 2: Preparing robot...")
            RobotDAO.wake_up()
            RobotDAO.say("I am ready to capture mathematical problems.")
            
            # Step 3: Capture image from robot camera
            print("📸 Step 3: Capturing image from robot camera...")
            capture_result = RobotDAO.capture_image(camera_id=1)  # Use bottom camera
            
            if not capture_result['success']:
                print(f"❌ Capture failed: {capture_result['error']}")
                RobotDAO.say("I couldn't capture the image. Please try again.")
                return False
            
            print(f"✅ Image captured: {capture_result['width']}x{capture_result['height']}")
            RobotDAO.say("Image captured successfully.")
            
            # Step 4: Send image data directly to API
            print("🔄 Step 4: Sending to Math Robot API...")
            api_result = ApiDAO.send_image_data(
                image_bytes=capture_result['image_bytes'],
                width=capture_result['width'],
                height=capture_result['height'],
                colorspace=capture_result['colorspace']
            )
            
            if not api_result['success']:
                print(f"❌ API processing failed: {api_result['error']}")
                RobotDAO.say("The mathematical processing service is unavailable.")
                return False
            
            api_data = api_result['data']
            print(f"✅ API processing successful. Found {api_data['total_problems']} problems.")
            RobotDAO.say(f"I found {api_data['total_problems']} mathematical problems.")
            
            # Step 5: Connect to Wolfram
            print("🔗 Step 5: Connecting to Wolfram Kernel...")
            if not WolframDAO.connect():
                print("❌ Failed to connect to Wolfram Kernel")
                RobotDAO.say("The mathematical solver is unavailable.")
                return False
            
            # Step 6: Process each problem with Wolfram
            print("🧮 Step 6: Evaluating with Wolfram...")
            processed_problems = PipelineService._process_with_wolfram(api_data['results'])
            
            # Step 7: Display and announce results
            print("📊 Step 7: Finalizing results...")
            PipelineService._display_results(processed_problems)
            PipelineService._announce_results(processed_problems)
            
            processing_time = time.time() - start_time
            print(f"✅ Pipeline completed in {processing_time:.2f} seconds")
            
            # Step 8: Clean up
            RobotDAO.say("Processing complete. I am going to rest now.")
            RobotDAO.rest()
            RobotDAO.disconnect()
            
            return True
            
        except Exception as e:
            print(f"❌ Pipeline failed: {e}")
            RobotDAO.say("An error occurred during processing.")
            RobotDAO.disconnect()
            return False
        finally:
            WolframDAO.disconnect()
    
    @staticmethod
    def _process_with_wolfram(api_results):
        """Process API results through Wolfram evaluation"""
        processed = []
        
        for problem in api_results:
            if problem['success'] and problem['latex']:
                print(f"   Processing Problem {problem['problem_id']}...")
                
                wolfram_result = WolframDAO.evaluate_expression(problem['latex'])
                
                processed_problem = problem.copy()
                processed_problem['wolfram_evaluation'] = wolfram_result
                processed.append(processed_problem)
            else:
                processed.append(problem)
        
        return processed
    
    @staticmethod
    def _display_results(results):
        """Display formatted results"""
        print("\n" + "="*70)
        print("📊 MATHEMATICAL PROCESSING RESULTS")
        print("="*70)
        
        successful_count = sum(1 for r in results if r.get('success', False))
        
        print(f"Total Problems: {len(results)}")
        print(f"Successfully Processed: {successful_count}")
        print(f"Failed: {len(results) - successful_count}")
        print("-" * 70)
        
        for result in results:
            status = "✅ SUCCESS" if result['success'] else "❌ FAILED"
            print(f"\n🔢 Problem {result['problem_id']} - {status}")
            
            if result['success']:
                print(f"   Original: {result['latex']}")
                if 'wolfram_evaluation' in result and result['wolfram_evaluation']['success']:
                    print(f"   Wolfram:  {result['wolfram_evaluation']['result']}")
                else:
                    wolfram_error = result.get('wolfram_evaluation', {}).get('error', 'No evaluation')
                    print(f"   Wolfram:  ❌ {wolfram_error}")
            else:
                print(f"   Error: {result.get('error', 'Unknown error')}")
    
    @staticmethod
    def _announce_results(results):
        """Announce results using robot speech"""
        successful = [r for r in results if r.get('success', False)]
        
        if successful:
            RobotDAO.say(f"I successfully processed {len(successful)} mathematical problems.")
            for i, result in enumerate(successful[:3]):  # Announce first 3 results
                if 'wolfram_evaluation' in result and result['wolfram_evaluation']['success']:
                    RobotDAO.say(f"Problem {i+1} has been solved.")
        else:
            RobotDAO.say("I couldn't process any mathematical problems from the image.")
    
    @staticmethod
    def check_system_health():
        """Check health of all system components"""
        print("🔍 Performing system health check...")
        
        # Check API
        api_health = ApiDAO.health_check()
        print(f"📡 API: {'✅ Available' if api_health else '❌ Unavailable'}")
        
        # Check Wolfram
        wolfram_health = WolframDAO.connect()
        if wolfram_health:
            WolframDAO.disconnect()
        print(f"🧮 Wolfram: {'✅ Available' if wolfram_health else '❌ Unavailable'}")
        
        # Check Robot
        robot_health = RobotDAO.connect()
        if robot_health:
            camera_info = RobotDAO.get_camera_info()
            RobotDAO.disconnect()
            print(f"🤖 Robot: ✅ Available")
            print("📷 Cameras:")
            for info in camera_info:
                print(f"   {info}")
        else:
            print(f"🤖 Robot: ❌ Unavailable (simulation mode only)")
        
        return api_health and wolfram_health