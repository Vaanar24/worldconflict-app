New-Item -Path app\__init__.py -ItemType File -Force
New-Item -Path app\api\__init__.py -ItemType File -Force
New-Item -Path app\core\__init__.py -ItemType File -Force
New-Item -Path app\models\__init__.py -ItemType File -Force
from app.api import events, cameras