import json
import sys

sys.stdout.reconfigure(encoding='utf-8')
lines = open('kernel_logs_new.txt', encoding='utf-8').readlines()

# Parse JSON log events or lines
for l in lines:
    try:
        data = json.loads(l.strip().lstrip(','))
        msg = data.get('data', '')
        if any(keyword in msg for keyword in ['ResNet50', 'ViT-B/16', 'ENSEMBLE', 'Accuracy', 'Macro-F1', 'QWK', 'Ngưỡng', 'Hoàn tất', 'Early Stopping']):
            print(msg.strip())
    except:
        if any(keyword in l for keyword in ['ResNet50', 'ViT-B/16', 'ENSEMBLE', 'Accuracy', 'Macro-F1', 'QWK', 'Ngưỡng', 'Hoàn tất', 'Early Stopping']):
            print(l.strip())
