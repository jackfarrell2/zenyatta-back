from django.db import models


def get_default_content():
    return {
        "type": "doc",
        "content": [
            {
                "type": "paragraph",
                "attrs": {
                    "lineHeight": "normal",
                    "textAlign": None
                }
            }
        ]
    }


class Process(models.Model):
    title = models.CharField(max_length=255)

    def __str__(self):
        return self.title


class Task(models.Model):
    title = models.CharField(max_length=255)
    process = models.ForeignKey(
        Process,
        on_delete=models.SET_NULL,
        related_name='tasks',
        null=True,
        blank=True
    )
    step_number = models.PositiveIntegerField()
    content = models.JSONField(default=get_default_content)
    is_leaf = models.BooleanField(default=True)
    linked_process = models.ForeignKey(
        Process,
        on_delete=models.SET_NULL,
        related_name='title_task',
        null=True,
        blank=True
    )

    def __str__(self):
        return self.title
