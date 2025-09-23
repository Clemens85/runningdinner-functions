import re
from UserRequest import PAGE_NAME_KEY, PUBLIC_EVENT_REGISTRATIONS_KEY
from logger.Log import Log

PUBLIC_EVENT_ID_KEY = "public_event_id"
ADMIN_ID_KEY = "admin_id"

class RequestParamsParser:

  @classmethod
  def parse(cls, request_params: dict[str, str]) -> dict[str, str]:
    url = request_params.get(PAGE_NAME_KEY)
    
    public_event_id = None
    admin_id = None

    Log.info(f"Parsing {url}")

    if url:
      match = re.search(r"/running-dinner-events/([^/]+)", url)
      if match:
        public_event_id = match.group(1)

    if request_params.get(PUBLIC_EVENT_REGISTRATIONS_KEY) and (public_event_id is None or len(public_event_id) == 0):
      public_event_ids_arr = request_params.get(PUBLIC_EVENT_REGISTRATIONS_KEY).split(",")
      Log.info(f"Got public event ids: {public_event_ids_arr}")
      if len(public_event_ids_arr) > 0:
        public_event_id = public_event_ids_arr[0]

    return { PUBLIC_EVENT_ID_KEY: public_event_id, ADMIN_ID_KEY: admin_id }
  