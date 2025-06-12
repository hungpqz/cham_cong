
app_name = "cham_cong"
app_title = "Cham Cong"
app_publisher = "OpenAI"
app_description = "Ứng dụng chấm công với dữ liệu từ máy chấm công"
app_email = "contact@example.com"
app_license = "MIT"

fixtures = ["Custom Field"]

doc_events = {}

override_whitelisted_methods = {
    "/api/method/cham_cong.api.cham_cong_handler": "cham_cong.api.cham_cong_handler"
}
override_whitelisted_methods = {
    "cham_cong.api.webhook.hikvision_webhook": "cham_cong.api.webhook.hikvision_webhook"
}