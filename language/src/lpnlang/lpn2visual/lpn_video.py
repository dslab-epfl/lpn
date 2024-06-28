
from .lpn_html import lpn_viz_graph_only
from ..lpn_simulate import lpn_sim_one_step
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
import time
import os
import shutil

def remove_directory(path):
    try:
        shutil.rmtree(path)
    except FileNotFoundError:
        pass
    except Exception as e:
        print(f"Error: {e}")


def html_to_image(html_files, output_folder):
    # Setup WebDriver
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")  # Run in headless mode
    driver = webdriver.Chrome(options=options)

    for i, html_file in enumerate(html_files):
        # Open the HTML file
        print(html_file)
        driver.get("file://" + html_file)
        time.sleep(0.1)  # Wait for the page to load completely
        # Save screenshot as PNG
        driver.save_screenshot(f"{output_folder}/screenshot_{i+1:04d}.png")

    driver.quit()

def lpn_visual_video(p_list, t_list, steps):
    # Create temporary directory
    
    tmp_dir = "/tmp/tmp_html"
    tmp_dir_pics = "/tmp/tmp_png"
    remove_directory(tmp_dir)
    remove_directory(tmp_dir_pics)
    os.makedirs(tmp_dir_pics, exist_ok=True)
    os.makedirs(tmp_dir, exist_ok=True)
    html_files = []
    clk = 0
    enabled_ts = []
    cnt = 0
    html_file = f"{tmp_dir}/_lpn_video_{cnt}.html"
    html_files.append(html_file)
    lpn_viz_graph_only(p_list, t_list, html_file, clk, None)
    cnt = 1
    for i in range(steps):
        while len(enabled_ts) > 0:
            t = enabled_ts[0]
            html_file = f"{tmp_dir}/_lpn_video_{cnt}.html"
            html_files.append(html_file)
            lpn_viz_graph_only(p_list, t_list, html_file, clk, t)
            enabled_ts.pop(0)
            cnt += 1
        clk, enabled_ts = lpn_sim_one_step(t_list)
        if clk == -1:
            break

    
    html_to_image(html_files, tmp_dir_pics)
    print("INFO: now creating video ... ")
    os.system(f"ffmpeg -r 2 -i {tmp_dir_pics}/screenshot_%04d.png -vcodec libx264 -crf 23 -pix_fmt yuv420p output_video.mp4")