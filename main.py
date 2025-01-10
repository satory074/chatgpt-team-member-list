import sys
import os
import re
import time
import pyautogui
import pyperclip

def main():
    # ------------------------------------
    # コマンドライン引数からページ数を取得
    # ------------------------------------
    if len(sys.argv) > 1:
        # python main.py 22 の場合 -> sys.argv[1] = "22"
        num_pages = int(sys.argv[1])
    else:
        # 引数が無ければデフォルト値 6 を使用
        num_pages = 6

    print(f"[INFO] Number of pages to process: {num_pages}")

    all_pages_members = []

    def extract_members(text):
        print("[DEBUG] Starting text extraction...")
        lines = text.splitlines()
        cleaned_lines = [l.strip() for l in lines if l.strip()]

        email_pattern = re.compile(r"[A-Za-z0-9._%+\-]+@[A-Za-z0-9.\-]+\.[A-Za-z]{2,}")
        records = []
        i = 0
        while i < len(cleaned_lines):
            name_line = cleaned_lines[i]
            email_line = cleaned_lines[i + 1] if (i + 1 < len(cleaned_lines)) else ""
            role_line = cleaned_lines[i + 2] if (i + 2 < len(cleaned_lines)) else ""

            # メール形式チェック & ロールが "メンバー"
            if role_line == "メンバー" and email_pattern.match(email_line):
                records.append((name_line, email_line, role_line))
                i += 3
            else:
                i += 1

        print(f"[DEBUG] Extracted {len(records)} member records from text.")
        return records

    # デバッグ用スクリーンショット関数
    def debug_screenshot():
        print("[DEBUG] Taking screenshot of current screen...")
        screenshot_path = "current_screen.png"
        pyautogui.screenshot(screenshot_path)
        if os.path.exists(screenshot_path):
            print(f"[DEBUG] Screenshot saved to {screenshot_path}")
        else:
            print("[DEBUG] Failed to save screenshot.")

    # ------------------------------------
    # 画像検索は使わず、座標クリックに変更する前提
    # ------------------------------------
    TARGET_X, TARGET_Y = 1164, 965  # ログなどから取得した座標

    print("[INFO] Starting in 5 seconds (countdown)...")
    for i in range(3, 0, -1):
        print(f"[INFO] {i}...")
        time.sleep(1)

    # ------------------------------------
    # メインループ: 指定ページ数だけ繰り返し
    # ------------------------------------
    for page in range(1, num_pages + 1):
        print(f"[INFO] ===== Page {page} / {num_pages} =====")

        # 全選択＆コピー（Windowsの場合: winleft + a / winleft + c）
        print("[INFO] Selecting all text (winleft + a) ...")
        pyautogui.hotkey("winleft", "a")
        time.sleep(0.5)

        print("[INFO] Copying to clipboard (winleft + c) ...")
        pyautogui.hotkey("winleft", "c")
        time.sleep(0.5)

        # クリップボードからテキストを取得
        print("[INFO] Reading text from clipboard...")
        copied_text = pyperclip.paste()
        print(f"[DEBUG] Clipboard text length: {len(copied_text)}")

        print("[INFO] Extracting member info from text...")
        members = extract_members(copied_text)
        all_pages_members.extend(members)

        # 次のページがある場合のみページ送り
        if page < num_pages:
            print(f"[INFO] Moving to next page (page {page+1})")

            screen_size = pyautogui.size()
            print(f"[DEBUG] Screen size: {screen_size}")
            mouse_pos = pyautogui.position()
            print(f"[DEBUG] Current mouse position: {mouse_pos}")

            for idx in range(1, 3):
                print(f"[INFO] Pressing PageDown #{idx}")
                pyautogui.press("pagedown")
                time.sleep(0.5)

            print(f"[INFO] Moving mouse to next button (X={TARGET_X}, Y={TARGET_Y})")
            pyautogui.moveTo(TARGET_X, TARGET_Y, duration=0.5)
            print("[INFO] Clicking next page button...")
            pyautogui.click()

            print("[INFO] Waiting 5 seconds for the page to load...")
            for i in range(5, 0, -1):
                print(f"[INFO] {i}...")
                time.sleep(1)

            print("[INFO] Pressing Home key to go to the top of the page...")
            pyautogui.press("home")

    # ------------------------------------
    # 結果の書き出し
    # ------------------------------------
    output_file = "members.txt"
    print(f"[INFO] Writing all member data to {output_file}...")
    with open(output_file, "w", encoding="utf-8") as f:
        f.write("名前,メール,ロール\n")
        for name, email, role in all_pages_members:
            f.write(f"{name},{email},{role}\n")

    print("[INFO] All pages processed successfully.")
    print(f"[INFO] Member list has been saved to {output_file}.")

    # ------------------------------------
    # members.txt をクリップボードへコピー
    # ------------------------------------
    try:
        with open(output_file, "r", encoding="utf-8") as f:
            members_data = f.read()
        pyperclip.copy(members_data)
        print("[INFO] The content of members.txt has been copied to the clipboard.")
    except Exception as e:
        print(f"[ERROR] Failed to copy {output_file} content to clipboard: {e}")

if __name__ == "__main__":
    main()
