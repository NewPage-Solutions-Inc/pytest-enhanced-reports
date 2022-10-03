import logging
import os
import dotenv
import allure
from allure_commons.types import AttachmentType
from PIL import Image
import cv2
import common_utils

dotenv.load_dotenv()

logger = logging.getLogger(__name__)


class ScreenRecorder:
    def __init__(self):
        self.stop = False
        self.directory = "temp/"  # This directory will be used to save the frames temporarily
        self.video_store = (
            "videos"  # This will be used to save the recorded video
        )

    def start_capturing(self, driver_):
        """This method will start capturing images and saving them on disk under /video folder
        These images will later be used to stich together into a video"""
        try:
            count = 0
            if not os.path.isdir(self.directory):
                os.mkdir(self.directory)
                logging.info("Creating new directory: " + self.directory)
            while True:
                driver_.save_screenshot(
                    self.directory + "/" + str(count) + ".png"
                )
                count += 1
                if self.stop:
                    logging.info("Stopping Screen Capture")
                    break
            logger.info(
                "SCREENSHOTS CAPTURED AND WRITTEN ON DISK: " + str(count)
            )
        except Exception as error:
            logger.error(
                "An Exception occurred while taking screenshot. " + str(error)
            )

    def create_video_from_images(
        self, scenario_info, location, video_size: tuple, frame_rate: int
    ):
        """This method will stitch the images under /video directory into a video"""
        fourcc = cv2.VideoWriter_fourcc(*"vp09")
        video_name = f"{location}/{scenario_info}.webm"
        video = cv2.VideoWriter(
            video_name, fourcc, int(frame_rate), video_size
        )
        images_path = [
            f for f in os.listdir(self.directory) if f.endswith(".png")
        ]
        images_path = sorted(
            images_path, key=lambda x: int(os.path.splitext(x)[0])
        )
        for img in images_path:
            if img.__contains__("png"):
                video.write(
                    cv2.resize(
                        cv2.imread(os.path.join(self.directory, img)),
                        video_size,
                    )
                )
        video.release()

        logger.info(
            "TEST EXECUTION VIDEO RECORDING VIDEO STOPPED [Video Size: "
            + str(video_size)
            + " - Frame Rate: "
            + str(frame_rate)
            + "]"
        )

        return video_name

    def stop_recording_and_stitch_video(
        self, video_info, recorder_thread, scenario_info, attachment_name
    ):
        try:
            self.stop = True
            recorder_thread.join()
            video_resize_info = self.get_video_resize_resolution(video_info)
            file_name = self.create_video_from_images(
                scenario_info,
                self.directory,
                video_resize_info,
                video_info["video_frame_rate"],
            )
            allure.attach.file(
                file_name,
                name=attachment_name,
                attachment_type=AttachmentType.WEBM,
            )

            if video_info["keep_videos"]:
                original_size = self.get_original_resolution(self.directory)
                self.create_video_from_images(
                    scenario_info,
                    self.video_store,
                    original_size,
                    video_info["video_frame_rate"],
                )

        except Exception as error:
            logger.error(
                "An Exception occurred while stitching video. " + str(error)
            )
        finally:
            # Now clean the images directory
            common_utils._clean_image_repository(self.directory)

    def get_video_resize_resolution(self, info):
        try:
            desired_resolution = None
            directory = self.directory
            if info:
                if info["video_width"] and info["video_height"]:
                    # if a resolution is provided, use that
                    desired_resolution = (
                        int(info["video_width"]),
                        int(info["video_height"]),
                    )
                elif info["video_resize_percentage"]:
                    # if a percentage is provided, set the resize factor from default to user provided value
                    resize_factor = int(info["video_resize_percentage"]) / 100
                    img = Image.open(
                        os.path.join(
                            directory,
                            [
                                f
                                for f in os.listdir(directory)
                                if f.endswith(".png")
                            ][0],
                        )
                    )
                    desired_resolution = common_utils._get_resized_resolution(
                        img.width, img.height, resize_factor
                    )
            return desired_resolution
        except Exception as error:
            logger.error(
                "An Exception occurred while fetching video resize resolution. "
                + str(error)
            )
            # Now clean the images in temp directory as video stitching has failed
            common_utils._clean_image_repository(self.directory)

    def get_original_resolution(self, directory):
        # get the original resolution of any screenshot from the screenshot repository
        img = Image.open(
            os.path.join(
                directory,
                [f for f in os.listdir(directory) if f.endswith(".png")][0],
            )
        )
        return img.width, img.height
