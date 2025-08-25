#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import subprocess
import sys
import shutil # Using shutil.move is slightly more robust than os.rename across filesystems

def check_ffmpeg():
    """Checks if ffmpeg is installed and accessible in the system PATH."""
    try:
        # Run ffmpeg -version, suppressing output, check return code
        subprocess.run(['ffmpeg', '-version'], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        print("✅ FFmpeg found.")
        return True
    except FileNotFoundError:
        print("❌ ERROR: 'ffmpeg' command not found.")
        print("   Please install FFmpeg (from https://ffmpeg.org/download.html)")
        print("   and ensure its 'bin' directory is added to your system's PATH.")
        return False
    except subprocess.CalledProcessError:
        # This might happen if ffmpeg exists but fails for some reason
        print("⚠️ Warning: 'ffmpeg -version' command failed, but ffmpeg might still exist.")
        print("   Proceeding, but errors may occur during video processing.")
        return True # Allow proceeding, but warn the user

def process_videos_in_directory(target_dir="."):
    """
    Processes MP4 files in the specified directory:
    1. Extracts the first frame as WebP (same name).
    2. Creates a subfolder named after the video (without extension).
    3. Moves the original MP4 and the generated WebP into the subfolder.
    """
    abs_target_dir = os.path.abspath(target_dir)
    print(f"📂 Starting processing in directory: {abs_target_dir}")

    if not os.path.isdir(abs_target_dir):
        print(f"❌ ERROR: Directory not found: {abs_target_dir}")
        return

    # Check for ffmpeg before starting the loop
    if not check_ffmpeg():
        return

    processed_files = 0
    error_files = 0

    # List items in the directory
    try:
        items = os.listdir(abs_target_dir)
    except OSError as e:
        print(f"❌ ERROR: Cannot list directory contents: {e}")
        return

    for item_name in items:
        item_path = os.path.join(abs_target_dir, item_name)

        # Process only files ending with .mp4 (case-insensitive)
        if os.path.isfile(item_path) and item_name.lower().endswith(".mp4"):
            base_name, _ = os.path.splitext(item_name)
            print(f"\n▶️ Processing video: {item_name}")

            # Define paths
            webp_filename = f"{base_name}.webp"
            temp_webp_path = os.path.join(abs_target_dir, webp_filename) # Create webp here first
            subfolder_path = os.path.join(abs_target_dir, base_name)
            final_video_path = os.path.join(subfolder_path, item_name)
            final_webp_path = os.path.join(subfolder_path, webp_filename)

            # --- Step 1: Extract First Frame as WebP ---
            try:
                # FFmpeg command:
                # -i : input file
                # -vf "select=eq(n\,0)" : video filter to select the first frame (index 0)
                #                      (backslash before comma might be needed depending on shell/OS)
                # -frames:v 1 : extract only one frame
                # -c:v libwebp : specify the WebP codec
                # -lossless 0 : use lossy compression (0=lossy, 1=lossless) - adjust if needed
                # -q:v 80 : quality for lossy WebP (0-100, higher is better/larger). Adjust!
                # -an : disable audio processing/output
                # -y : overwrite output file without asking
                ffmpeg_command = [
                    'ffmpeg',
                    '-i', item_path,
                    '-vf', r'select=eq(n\,0)', # Raw string helps with backslash
                    '-frames:v', '1',
                    '-c:v', 'libwebp',
                    '-lossless', '0', # Set to 1 for lossless
                    '-q:v', '80',     # Quality (0-100) for lossy. Ignored if lossless=1
                    '-an',
                    '-y',
                    temp_webp_path
                ]
                print(f"  🔧 Running FFmpeg: {' '.join(ffmpeg_command)}")
                result = subprocess.run(ffmpeg_command, check=True, capture_output=True, text=True, encoding='utf-8')
                print(f"  🖼️ Successfully extracted frame to: {webp_filename}")

                # --- Step 2: Create Subfolder and Move Files ---
                try:
                    # Create subdirectory (does nothing if it already exists)
                    os.makedirs(subfolder_path, exist_ok=True)
                    print(f"  📁 Ensured directory exists: {base_name}/")

                    # Move MP4 video file
                    print(f"  ➡️ Moving {item_name} to {base_name}/")
                    shutil.move(item_path, final_video_path)

                    # Move WebP image file
                    print(f"  ➡️ Moving {webp_filename} to {base_name}/")
                    shutil.move(temp_webp_path, final_webp_path)

                    print(f"  ✅ Successfully processed and moved files for: {base_name}")
                    processed_files += 1

                except OSError as e:
                    print(f"  ❌ ERROR creating directory or moving files for '{base_name}': {e}")
                    error_files += 1
                    # Attempt cleanup: Remove the generated webp if it still exists in the parent dir
                    if os.path.exists(temp_webp_path):
                        try:
                            os.remove(temp_webp_path)
                            print(f"  🧹 Cleaned up temporary file: {webp_filename}")
                        except OSError as rm_err:
                            print(f"  ⚠️ Warning: Could not remove temporary file {webp_filename}: {rm_err}")

            except subprocess.CalledProcessError as e:
                print(f"  ❌ ERROR running FFmpeg for '{item_name}':")
                print(f"     Command: {' '.join(e.cmd)}")
                print(f"     Return Code: {e.returncode}")
                # Limit potentially long stderr output
                stderr_output = e.stderr.strip()
                if len(stderr_output) > 500:
                     stderr_output = stderr_output[:250] + "\n...\n" + stderr_output[-250:]
                print(f"     Stderr: {stderr_output}")
                error_files += 1
            except Exception as e:
                print(f"  ❌ An unexpected error occurred processing '{item_name}': {e}")
                error_files += 1

    print("\n🏁 Processing Finished!")
    print(f"   Processed successfully: {processed_files} video(s)")
    print(f"   Encountered errors: {error_files} video(s)")

# --- Main execution block ---
if __name__ == "__main__":
    # By default, process videos in the same directory as the script.
    # You can change this to a specific path if needed, e.g., "/path/to/your/videos"
    script_directory = os.path.dirname(os.path.abspath(__file__))
    target_video_directory = script_directory # Or "." for current working dir, or specify a path

    # Optional: uncomment below to ask the user for the directory
    # user_input_dir = input(f"Enter target directory path (leave blank to use script's directory: {script_directory}): ")
    # if user_input_dir.strip():
    #     target_video_directory = user_input_dir.strip()

    process_videos_in_directory(target_video_directory)

    # Keep console open on Windows if run by double-clicking
    if sys.platform == "win32":
        input("\nPress Enter to exit...")