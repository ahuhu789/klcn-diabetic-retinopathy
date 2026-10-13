class ApiEndpoints {
  // Hugging Face Cloud 24/7 Serverless (Toàn cầu, không phụ thuộc máy tính ở nhà)
  static const String hfCloudUrl =
      'https://slyviee-klcn-diabetic-retinopathy.hf.space';

  // Cloudflare Tunnel dự phòng
  static const String defaultCloudflareUrl =
      'https://followed-position-wisconsin-diesel.trycloudflare.com';

  // URL kết nối mạng nội bộ Wi-Fi (Máy tính và điện thoại cùng mạng Wi-Fi)
  static const String wifiLanUrl = 'http://192.168.1.175:8000';

  // URL dự phòng cho máy ảo Android Emulator
  static const String emulatorUrl = 'http://10.0.2.2:8000';

  // URL dự phòng cho Windows Desktop / Cục bộ
  static const String localhostUrl = 'http://127.0.0.1:8000';

  // Khóa lưu SharedPreferences
  static const String prefBaseUrlKey = 'custom_base_url';

  // Endpoints API
  static const String predict = '/api/predict';
  static const String samples = '/api/samples';
  static const String health = '/api/health';
}
