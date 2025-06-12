import frappe
import json
from frappe.utils import get_datetime

@frappe.whitelist(allow_guest=True)
def hikvision_webhook():
    try:
        # Lấy dữ liệu gốc từ HTTP POST
        content_type = frappe.request.content_type
        data = {}

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

        # Phân tích dữ liệu
        event = data.get("AccessControllerEvent", {})
        sub_event = event.get("AccessControllerEvent", {})

        employee_id = sub_event.get("employeeNoString")
        full_name = sub_event.get("name")
        date_time_raw = event.get("dateTime")

        if not employee_id or not date_time_raw:
            return {"status": "ignored", "reason": "Missing employeeNoString or dateTime"}

        # Xử lý thời gian
        from dateutil import parser
        parsed_dt = parser.parse(date_time_raw)
        datetime_obj = parsed_dt.replace(tzinfo=None)
        date_only = datetime_obj.date()

        # Kiểm tra đã có bản ghi trong ngày chưa
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
