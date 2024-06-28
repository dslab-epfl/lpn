
from lpn_html import lpn_viz_graph_only
from ..lpn_simulate import lpn_sim_one_step
from selenium import webdriver
import time
import os

def html_to_image(html_files, output_folder):
    # Setup WebDriver
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")  # Run in headless mode
    driver = webdriver.Chrome(executable_path='path_to_chromedriver', options=options)

    for i, html_file in enumerate(html_files):
        # Open the HTML file
        driver.get("file://" + html_file)
        time.sleep(1)  # Wait for the page to load completely

        # Save screenshot as PNG
        driver.save_screenshot(f"{output_folder}/screenshot_{i+1:04d}.png")

    driver.quit()

def lpn_visual_video(p_list, t_list, steps):
    # Create temporary directory
    
    tmp_dir = "tmp_html"
    os.makedirs(tmp_dir, exist_ok=True)
    html_files = []
    for i in range(steps):
        html_file = f"_lpn_video_{i}.html"
        html_files.append(html_file)
        lpn_viz_graph_only(p_list, t_list, html_file)
        if lpn_sim_one_step(t_list) == -1:
            break

    tmp_dir_pics = "tmp_png"
    os.makedirs(tmp_dir_pics, exist_ok=True)
    html_to_image(html_files, tmp_dir_pics)
    os.system(f"ffmpeg -r 1 -i {tmp_dir_pics}/screenshot_%04d.png -vcodec mpeg4 -y video.mp4")