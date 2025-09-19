import re
from UserRequest import URL_KEY

PUBLIC_EVENT_ID_KEY = "public_event_id"
ADMIN_ID_KEY = "admin_id"

class RequestParamsParser:

  @classmethod
  def parse(cls, request_params: dict[str, str]) -> dict[str, str]:
    url = request_params.get(URL_KEY)
    
    public_event_id = None
    admin_id = None
    
    if url:
      match = re.search(r"/running-dinner-events/([^/]+)", url)
      if match:
        public_event_id = match.group(1)
   
    return { PUBLIC_EVENT_ID_KEY: public_event_id, ADMIN_ID_KEY: admin_id }
  