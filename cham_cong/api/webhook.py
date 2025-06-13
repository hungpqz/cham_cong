import frappe
import json
from frappe.utils import get_datetime

@frappe.whitelist(allow_guest=True)
def hikvision_webhook():
    try:
        from dateutil import parser

        content_type = frappe.request.content_type
        data = {}

        # Lấy dữ liệu từ request
        if "application/json" in content_type:
            data = frappe.request.get_json()
        elif "multipart/form-data" in content_type:
            form_data = frappe.form_dict
            if "AccessControllerEvent" in form_data and isinstance(form_data["AccessControllerEvent"], str):
                data["AccessControllerEvent"] = json.loads(form_data["AccessControllerEvent"])
            else:
                data = form_data
        else:
            frappe.throw("Unsupported Content-Type")

        # Trường hợp dữ liệu đến từ máy khác: dạng {"event_log": "{...}"}
        if "event_log" in data and isinstance(data["event_log"], str):
            try:
                event = json.loads(data["event_log"])
            except json.JSONDecodeError:
                return {"status": "error", "message": "Invalid JSON in event_log"}
        else:
            event = data.get("AccessControllerEvent", {})

        sub_event = event.get("AccessControllerEvent", {})

        employee_id = (sub_event.get("employeeNoString") or "").strip()
        full_name = (sub_event.get("name") or "").strip()
        date_time_raw = (event.get("dateTime") or "").strip()

        if not employee_id or not date_time_raw:
            return {"status": "ignored", "reason": "Missing employeeNoString or dateTime"}

        # Parse datetime
        parsed_dt = parser.parse(date_time_raw)
        datetime_obj = parsed_dt.replace(tzinfo=None)
        date_only = datetime_obj.date()

        # Kiểm tra bản ghi chấm công đã có chưa
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
        frappe.log_error(frappe.get_traceback(), "Hikvision Webhook Error")
        return {"status": "error", "message": str(e)}
