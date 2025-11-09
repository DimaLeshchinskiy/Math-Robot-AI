from wolframclient.evaluation import WolframLanguageSession
from wolframclient.language import wl, wlexpr
from config import Config

class WolframDAO:
    """Data Access Object for Wolfram Kernel communication - Singleton with static methods"""
    
    _session = None
    _kernel_path = Config.WOLFRAM_KERNEL_PATH
    
    @staticmethod
    def connect():
        """Establish connection to Wolfram Kernel"""
        try:
            WolframDAO._session = WolframLanguageSession(WolframDAO._kernel_path)
            return True
        except Exception as e:
            print(f"Failed to connect to Wolfram Kernel: {e}")
            return False
    
    @staticmethod
    def disconnect():
        """Close Wolfram Kernel connection"""
        if WolframDAO._session:
            WolframDAO._session.terminate()
            WolframDAO._session = None
    
    @staticmethod
    def evaluate_expression(latex_expression):
        """
        Evaluate mathematical expression using Wolfram
        
        Args:
            latex_expression: LaTeX string to evaluate
            
        Returns:
            Dictionary with evaluation result
        """
        if not WolframDAO._session:
            return {
                'success': False,
                'error': 'Wolfram Kernel not connected'
            }
        
        try:
            result = WolframDAO._session.evaluate(
                wlexpr(f'ToString[TeXForm[ToExpression["{latex_expression}", TeXForm]]]')
            )
            
            return {
                'success': True,
                'result': result,
                'original_expression': latex_expression
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f"Wolfram evaluation failed: {str(e)}",
                'original_expression': latex_expression
            }
    
    @staticmethod
    def is_connected():
        """Check if Wolfram Kernel is connected"""
        return WolframDAO._session is not None