import sys 
sys.path.insert(0, r'D:\Sam\Vgas Shooping Ai\backend') 
from app.main import app 
print([route.path for route in app.routes]) 
