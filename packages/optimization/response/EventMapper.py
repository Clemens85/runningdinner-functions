class EventMapper:

  def __init__(self, admin_id: str, optimization_id: str):
      self.admin_id = admin_id
      self.optimization_id = optimization_id

  def new_optimization_finished_event(self):
      return {
        "adminId": self.admin_id,
        "optimizationId": self.optimization_id
      }

  def new_optimization_error_event(self, error_message: str):
      return {
        "adminId": self.admin_id,
        "optimizationId": self.optimization_id,
        "errorMessage": error_message
      }
