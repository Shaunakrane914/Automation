import traceback
import undetected_chromedriver as uc
try:
    print("Initializing UC...")
    driver = uc.Chrome()
    print("UC started.")
    driver.quit()
except Exception as e:
    with open("crash_out.txt", "w", encoding="utf-8") as f:
        f.write(traceback.format_exc())
    print("Crash saved to crash_out.txt")
