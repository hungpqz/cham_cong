
app_name = "cham_cong"
app_title = "Cham Cong"
app_publisher = "HungPQ"
app_description = "Ứng dụng chấm công với dữ liệu từ máy chấm công"
app_email = "hung.pham@wellspringsaigon.edu.vn"
app_license = "MIT"

fixtures = ["Custom Field"]

doc_events = {}

override_whitelisted_methods = {
    "/api/method/cham_cong.api.cham_cong_handler": "cham_cong.api.cham_cong_handler"
}
override_whitelisted_methods = {
    "cham_cong.api.webhook.hikvision_webhook": "cham_cong.api.webhook.hikvision_webhook"
}

# Để Frappe biết routes custom ở đâu
website_routes = "cham_cong.config.routes"
