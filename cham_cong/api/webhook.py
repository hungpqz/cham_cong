import frappe
import json
from frappe.utils import get_datetime

@frappe.whitelist(allow_guest=True)
def hikvision_webhook():
    try:
        from dateutil import parser

        event = {}
        sub_event = {}

        # 1. Nếu là multipart/form-data và có event_log
        if frappe.form_dict.get("event_log"):
            try:
                event = json.loads(frappe.form_dict["event_log"])
                sub_event = event.get("AccessControllerEvent", {})
            except Exception:
                return {"status": "error", "message": "Invalid JSON in event_log"}

        # 2. Nếu là multipart/form-data với AccessControllerEvent (máy khác)
        elif frappe.form_dict.get("AccessControllerEvent"):
            try:
                event = json.loads(frappe.form_dict["AccessControllerEvent"])
                sub_event = event.get("AccessControllerEvent", {})
            except Exception:
                return {"status": "error", "message": "Invalid JSON in AccessControllerEvent"}

        # 3. Nếu là application/json (POST raw body)
        else:
            try:
                data = frappe.request.get_json()
                event = data.get("AccessControllerEvent", {})
                sub_event = event.get("AccessControllerEvent", {})
            except Exception:
                return {"status": "error", "message": "Cannot parse JSON"}

        # Trích dữ liệu cần
        employee_id = (sub_event.get("employeeNoString") or "").strip()
        full_name = (sub_event.get("name") or "").strip()
        date_time_raw = (event.get("dateTime") or "").strip()

        if not employee_id or not date_time_raw:
            return {"status": "ignored", "reason": "Missing employeeNoString or dateTime"}

        parsed_dt = parser.parse(date_time_raw)
        datetime_obj = parsed_dt.replace(tzinfo=None)
        date_only = datetime_obj.date()

        existing_record = frappe.get_all(
            "Cham Cong",
            filters={
                "employee_id": employee_id,
                "date": date_only
            },
            fields=["name"]
        )

        if not existing_record:
            doc = frappe.new_doc("Cham Cong")
            doc.employee_id = employee_id
            doc.full_name = full_name
            doc.date = date_only
            doc.check_in_time = datetime_obj
            doc.insert(ignore_permissions=True)
            frappe.db.commit()
            return {"status": "success", "message": "Check-in recorded"}
        else:
            doc = frappe.get_doc("Cham Cong", existing_record[0].name)
            doc.check_out_time = datetime_obj
            doc.save(ignore_permissions=True)
            frappe.db.commit()
            return {"status": "success", "message": "Check-out updated"}

    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "Cham Cong Webhook Error")
        return {"status": "error", "message": str(e)}
