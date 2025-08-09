from django.utils import timezone

# пока что не рабочий, логика пока что в apps/blog/views.py
class MassCreation:
  def specify_data(data):
    pass

  def mass_creation(serializer_class, data):
    serializer = serializer_class(data=data, many=True)
    serializer.is_valid(raise_exception=True)
    return serializer
  
  def mass_update(self, request, *args, **kwargs):
    now = timezone.now()
    data = request.data
    for item in data:
      item['updated_at'] = now
      serializer = self.get_serializer(data=data, many=True)

    serializer = self.get_serializer(data=data, many=True)
    serializer.is_valid(raise_exception=True)
    self.perform_bulk_update(serializer)