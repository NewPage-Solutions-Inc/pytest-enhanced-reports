import logging
import os
import dotenv
import threading
import pytest
from pytest import fixture
import allure
from allure_commons.types import AttachmentType
from PIL import Image
import cv2
import enhanced_allure

dotenv.load_dotenv()

logger = logging.getLogger(__name__)


@pytest.fixture
def screen_recorder(report_video_recording_options):
    obj = ScreenRecorder()
    obj.video_store = report_video_recording_options["video_dir"]
    enhanced_allure._mkdir(obj.video_store)
    yield obj


@pytest.fixture
def video_capture_thread(screen_recorder, selenium):
    recorder_thread = threading.Thread(target=screen_recorder.start_capturing, name='Recorder', args=[selenium])
    yield recorder_thread, screen_recorder


@fixture(scope="session")
def report_video_recording_options(request) -> dict:
    cmd_line_plugin_options: dict = {
        "video_recording": request.config.getoption("report_video_recording"),
        "video_dir": request.config.getoption("report_video_dir"),
        "video_width": request.config.getoption("report_video_width"),
        "video_height": request.config.getoption("report_video_height"),
        "video_frame_rate": request.config.getoption("report_video_frame_rate"),
        "video_resize_percentage": request.config.getoption("report_video_resize_percentage"),
        "keep_videos": request.config.getoption("report_keep_videos")
    }

    env_plugin_options: dict = {
        "video_recording": enhanced_allure._get_env_var("REPORT_VIDEO_RECORDING", default_value=False),
        "video_dir": enhanced_allure._get_env_var("REPORT_VIDEO_DIR", default_value="videos"),
        "video_width": enhanced_allure._get_env_var("REPORT_VIDEO_WIDTH"),
        "video_height": enhanced_allure._get_env_var("REPORT_VIDEO_HEIGHT"),
        "video_frame_rate": enhanced_allure._get_env_var("REPORT_VIDEO_FRAME_RATE", default_value=5),
        "video_resize_percentage": enhanced_allure._get_env_var("REPORT_VIDEO_RESIZE_PERCENTAGE", default_value=30),
        "keep_videos": enhanced_allure._get_env_var("REPORT_KEEP_VIDEOS", default_value=False)
    }

    video_recording = None
    video_height = None
    video_width = None
    video_frame_rate = None
    video_resize_percentage = None
    video_dir = None
    keep_videos = None

    if cmd_line_plugin_options['video_recording']:
        video_recording = str(cmd_line_plugin_options['video_recording']).lower() == 'true'
    else:
        video_recording = str(env_plugin_options['video_recording']).lower() == 'true'

    if cmd_line_plugin_options['video_dir']:
        video_dir = cmd_line_plugin_options['video_dir']
    else:
        video_dir = env_plugin_options['video_dir']

    if cmd_line_plugin_options['video_frame_rate']:
        video_frame_rate = cmd_line_plugin_options['video_frame_rate']
    elif env_plugin_options['video_frame_rate']:
        video_frame_rate = env_plugin_options['video_frame_rate']

    if cmd_line_plugin_options['keep_videos']:
        keep_videos = str(cmd_line_plugin_options['keep_videos']).lower() == 'true'
    else:
        keep_videos = str(env_plugin_options['keep_videos']).lower() == 'true'

    if cmd_line_plugin_options['video_width'] and cmd_line_plugin_options['video_height']:
        video_width = cmd_line_plugin_options['video_width']
        video_height = cmd_line_plugin_options['video_height']
    elif env_plugin_options['video_width'] and env_plugin_options['video_height']:
        video_width = env_plugin_options['video_width']
        video_height = env_plugin_options['video_height']
    else:
        if cmd_line_plugin_options['video_resize_percentage']:
            video_resize_percentage = cmd_line_plugin_options['video_resize_percentage']
        elif env_plugin_options['video_resize_percentage']:
            video_resize_percentage = env_plugin_options['video_resize_percentage']

    return {
        "video_recording": video_recording,
        "video_dir": video_dir,
        "video_height": video_height,
        "video_width": video_width,
        "video_frame_rate": video_frame_rate,
        "video_resize_percentage": video_resize_percentage,
        "keep_videos": keep_videos
    }


class ScreenRecorder:

    def __init__(self):
        self.stop = False
        self.directory = "temp/"  # This directory will be used to save the frames temporarily
        self.video_store = "videos"  # This will be used to save the recorded video

    def start_capturing(self, driver_):
        """This method will start caotyring images and saving them on disk under /video folder
            These images will later be used to stich together into a video"""
        try:
            count = 0
            if not os.path.isdir(self.directory):
                os.mkdir(self.directory)
                logging.info("Creating new directory: " + self.directory)
            while True:
                driver_.save_screenshot(self.directory+"/"+str(count)+".png")
                count += 1
                if self.stop:
                    logging.info("Stopping Screen Capture")
                    break
            logger.info("SCREENSHOTS CAPTURED AND WRITTEN ON DISK: " + str(count))
        except Exception as error:
            logger.error("An Exception occurred while taking screenshot. " + str(error))

    def create_video_from_images(self, scenario_info, video_size: tuple, frame_rate: int, keep_videos):
        """This method will sticth the images under /video directory into a video"""
        try:
            fourcc = cv2.VideoWriter_fourcc(*'vp09')
            video_name = f"{self.video_store}/{scenario_info}.webm"
            video = cv2.VideoWriter(video_name, fourcc, int(frame_rate), video_size)
            images_path = os.listdir(self.directory)
            images_path = sorted(images_path, key=lambda x: int(os.path.splitext(x)[0]))
            for img in images_path:
                if img.__contains__('png'):
                    video.write(cv2.resize(cv2.imread(self.directory + img), video_size))
            video.release()
            logger.info("TEST EXECUTION VIDEO RECORDING VIDEO STOPPED [Video Size: " + str(video_size) + " - Frame Rate: " + str(frame_rate) + "]")
            return video_name
        except Exception as error:
            logger.error("An Exception occurred while stitching video. " + str(error))
        finally:
            # Now clean the images directory
            if not keep_videos:
                enhanced_allure._clean_image_repository(self.directory)

    def stop_recording_and_stitch_video(self, video_info, recorder_thread, scenario_info, attachment_name):
        self.stop = True
        recorder_thread.join()
        video_resize_info = _get_video_resize_resolution(video_info, self)
        file_name = self.create_video_from_images(scenario_info, video_resize_info, video_info['video_frame_rate'],
                                                  video_info['keep_videos'])
        allure.attach.file(file_name, name=attachment_name, attachment_type=AttachmentType.WEBM)


def _get_video_resize_resolution(info, recorder):
    try:
        desired_resolution = None
        directory = recorder.directory
        if info:
            if info['video_width'] and info['video_height']:
                # if a resolution is provided, use that
                desired_resolution = (int(info['video_width']), int(info['video_height']))
            elif info['video_resize_percentage']:
                # if a percentage is provided, set the resize factor from default to user provided value
                resize_factor = int(info['video_resize_percentage']) / 100
                img = Image.open(os.path.join(directory, os.listdir(directory)[0]))
                desired_resolution = enhanced_allure.__get_resized_resolution(img.width, img.height, resize_factor)
        return desired_resolution
    except Exception as error:
        logger.error("An Exception occurred while fetching video resize resolution. " + str(error))
        # Now clean the images in temp directory as video stitching has failed
        enhanced_allure._clean_image_repository(recorder.directory)

