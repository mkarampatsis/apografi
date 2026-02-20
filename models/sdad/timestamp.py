from datetime import datetime
import mongoengine as me

class TimeStampedModel(me.Document):
  meta = {'abstract': True}
  createdAt = me.DateTimeField(default=datetime.now())
  updatedAt = me.DateTimeField(default=datetime.now())

  def save(self, *args, **kwargs):
    if not self.createdAt:
      self.createdAt = datetime.now()
    self.updatedAt = datetime.now()
    return super().save(*args, **kwargs)