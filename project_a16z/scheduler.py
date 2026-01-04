import time
import subprocess

INTERVAL_MINUTES = 60  # запуск каждый час

def run():
    while True:
        print("=== Запуск мониторинга a16z ===")
        subprocess.run(["python", "main.py"])
        print(f"Ожидание {INTERVAL_MINUTES} минут...\n")
        time.sleep(INTERVAL_MINUTES * 60)

if __name__ == "__main__":
    run()
