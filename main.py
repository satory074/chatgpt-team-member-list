import os
import re
import time

import pyautogui
import pyperclip

next_button_image = "next_button.png"
num_pages = 6
all_pages_members = []


def extract_members(text):
    lines = text.splitlines()
    cleaned_lines = [l.strip() for l in lines if l.strip()]

    email_pattern = re.compile(r"[A-Za-z0-9._%+\-]+@[A-Za-z0-9.\-]+\.[A-Za-z]{2,}")
    records = []
    i = 0
    while i < len(cleaned_lines):
        name_line = cleaned_lines[i]

        if i + 1 < len(cleaned_lines):
            email_line = cleaned_lines[i + 1]
        else:
            email_line = ""

        if i + 2 < len(cleaned_lines):
            role_line = cleaned_lines[i + 2]
        else:
            role_line = ""

        # メール形式チェック & ロールが "メンバー"
        if role_line == "メンバー" and email_pattern.match(email_line):
            records.append((name_line, email_line, role_line))
            i += 3
        else:
            i += 1

    return records


def debug_screenshot():
    """
    デバッグ用に現在の画面をスクリーンショットし保存。
    """
    print("[DEBUG] Taking screenshot of current screen...")
    screenshot_path = "current_screen.png"
    pyautogui.screenshot(screenshot_path)
    if os.path.exists(screenshot_path):
        print(f"[DEBUG] Screenshot saved to {screenshot_path}")
    else:
        print("[DEBUG] Failed to save screenshot.")


def safe_locate_on_screen(image, confidence=0.9):
    """
    ImageNotFoundExceptionが発生した場合Noneを返す安全なlocateOnScreen
    """
    try:
        return pyautogui.locateOnScreen(image, confidence=confidence)
    except pyautogui.ImageNotFoundException:
        return None


def try_locate_image(image_path, confidences, scroll_steps=0, scroll_amount=-300):
    """
    画像マッチングを複数のconfidence値で試し、スクロールも行う。
    confidences: confidence値のリスト(高→低)で試す
    scroll_steps: スクロール試行回数
    scroll_amount: 一回のscrollで動かす距離(-300は下方向)
    """
    for conf in confidences:
        print(f"[DEBUG] Trying locateOnScreen with confidence={conf}")
        loc = safe_locate_on_screen(image_path, confidence=conf)
        if loc:
            return loc

        # スクロールしながら探す
        for attempt in range(scroll_steps):
            pyautogui.scroll(scroll_amount)
            time.sleep(1)
            loc = safe_locate_on_screen(image_path, confidence=conf)
            if loc:
                return loc

    return None


for i in range(5, 0, -1):
    print(i + 1)
    time.sleep(1)

for page in range(1, num_pages + 1):
    # Chromeウィンドウアクティブ化
    # chrome_windows = [w for w in gw.getAllWindows() if "Google Chrome" in w.title]
    # if not chrome_windows:
        # print("[ERROR] Google Chromeウィンドウが見つかりません。")
        # break

    # chrome_window = chrome_windows[0]
    # chrome_window.activate()

    # 全選択＆コピー（キーマップを考慮してwinleft使用）
    pyautogui.hotkey("winleft", "a")
    time.sleep(0.5)
    pyautogui.hotkey("winleft", "c")
    time.sleep(0.5)

    copied_text = pyperclip.paste()
    members = extract_members(copied_text)
    all_pages_members.extend(members)

    if page < num_pages:
        print(f"[INFO] Searching next page button on page {page}")

        # デバッグ情報
        screen_size = pyautogui.size()
        print(f"[DEBUG] Screen size: {screen_size}")
        mouse_pos = pyautogui.position()
        print(f"[DEBUG] Current mouse position: {mouse_pos}")
        print("[DEBUG] Checking if next_button.png exists in current directory:", os.path.exists(next_button_image))

        confidences = [0.7, 0.6]

        next_button_location = try_locate_image(next_button_image, confidences, scroll_steps=5, scroll_amount=-300)

        if not next_button_location:
            print("[WARN] Next page button not found, taking debug screenshot...")
            debug_screenshot()
            print("[ERROR] Could not locate next page button after multiple attempts.")
            break

        next_center = pyautogui.center(next_button_location)
        print(f"[DEBUG] Next button found at: {next_button_location}, center: {next_center}")

        pyautogui.moveTo(next_center, duration=0.5)
        pyautogui.click()

        print("[INFO] Clicked next page button, waiting for page to load...")
        time.sleep(5)  # 待機時間を増やす
        pyautogui.press("home")  # ページの先頭へ戻る

output_file = "members.txt"
with open(output_file, "w", encoding="utf-8") as f:
    f.write("名前,メール,ロール\n")
    for name, email, role in all_pages_members:
        f.write(f"{name},{email},{role}\n")

print("[INFO] すべてのページからデータを取得しました。")
print(f"[INFO] メンバー一覧は {output_file} に出力されました。")
