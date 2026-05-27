from sdp_client import ServiceDeskPlusClient
client = ServiceDeskPlusClient.from_env()
print("✅ Client khởi tạo xong")
print(client.config.SDP_BASE_URL)
print(client.config.SDP_API_KEY[:8]+"...")
