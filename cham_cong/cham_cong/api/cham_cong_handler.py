
import frappe
from frappe.utils import get_datetime

@frappe.whitelist(allow_guest=True)
def cham_cong_handler():
    import json
    data = frappe.local.form_dict
    if isinstance(data, str):
        data = json.loads(data)

    try:
        event = data.get("AccessControllerEvent", {})
        nested_event = event.get("AccessControllerEvent", {})

        employee_id = nested_event.get("employeeNoString")
        full_name = nested_event.get("name")
        datetime_str = event.get("dateTime")
        datetime_obj = get_datetime(datetime_str)
        date_only = datetime_obj.date()

        existing_record = frappe.get_all(
            "Cham Cong",
            filters={
                "employee_id": employee_id,
                "date": date_only
            },
            fields=["name", "check_in_time", "check_out_time"]
        )

        if not existing_record:
            doc = frappe.new_doc("Cham Cong")
            doc.employee_id = employee_id
            doc.full_name = full_name
            doc.check_in_time = datetime_obj
            doc.date = date_only
            doc.insert(ignore_permissions=True)
            frappe.db.commit()
            return {"status": "success", "message": "Check-in recorded."}
        else:
            record_name = existing_record[0]["name"]
            doc = frappe.get_doc("Cham Cong", record_name)
            doc.check_out_time = datetime_obj
            doc.save(ignore_permissions=True)
            frappe.db.commit()
            return {"status": "success", "message": "Check-out updated."}

    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "Cham Cong Error")
        return {"status": "error", "message": str(e)}
