def setup_rec_schedule():
    from c2_wrapper import create_custom_field, create_hook
    from initialize.create_objects import create_recurring_job

    rec_schedule = {
        "name": "rec_schedule",
        "label": "rec_schedule",
        "type": "Code",
    }
    cf = create_custom_field(**rec_schedule)

    rec_job_action = {
        "name": "REC Activity",
        "description": ("Recurring job to delete, create or continue with rec."),
        "hook_point": None,
        "module": "/var/opt/cloudbolt/proserv/xui/create_recurring_job/schedule_reccuring_job.py",
    }

    rec_job_job = {
        "name": "REC Activity Job",
        "enabled": True,
        "description": """
            Recurring job to delete, create or continue with rec.
        """,
        "type": "recurring_action",
        "hook_name": "Rec Hook",
        "schedule": "0 * * * *",
    }
    create_hook(**rec_job_action)
    create_recurring_job(**rec_job_job)

    return cf
