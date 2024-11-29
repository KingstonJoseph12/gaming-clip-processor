from moviepy.editor import *
import cv2
import numpy as np
import os
import shutil
import argparse
from pathlib import Path

def process_videos(input_dir, output_dir, archive_dir, twitter_outro, youtube_outro):
    """
    Process video files to create both YouTube Shorts and Twitter formats
    
    Args:
        input_dir (str): Directory containing input videos
        output_dir (str): Base directory for output videos
        archive_dir (str): Directory for archiving processed videos
        twitter_outro (str): Path to Twitter outro video
        youtube_outro (str): Path to YouTube outro video
    """
    # Create output directories if they don't exist
    yt_output = os.path.join(output_dir, "youtube")
    twitter_output = os.path.join(output_dir, "twitter")
    os.makedirs(yt_output, exist_ok=True)
    os.makedirs(twitter_output, exist_ok=True)
    os.makedirs(archive_dir, exist_ok=True)

    # Get all MP4 files from input directory
    video_files = [f for f in os.listdir(input_dir) if f.endswith(".mp4")]

    for video_file in video_files:
        video_path = os.path.join(input_dir, video_file)
        filename = os.path.basename(video_path).replace(" ", "_")

        # Process Twitter version
        create_twitter_video(video_path, twitter_outro, twitter_output, filename)

        # Process YouTube version
        create_youtube_video(video_path, youtube_outro, yt_output, filename)

        # Archive the input file
        shutil.copy(video_path, archive_dir)

def create_twitter_video(video_path, outro_path, output_dir, filename):
    """Create Twitter format video"""
    main_video = VideoFileClip(video_path)
    outro = VideoFileClip(outro_path)
    
    final_video = concatenate_videoclips([main_video, outro])
    
    output_path = os.path.join(output_dir, f"Twitter_{filename}")
    final_video.write_videofile(output_path, codec='libx264', bitrate='50M')
    
    main_video.close()
    outro.close()
    final_video.close()

def create_youtube_video(video_path, outro_path, output_dir, filename):
    """Create YouTube Shorts format video with blur effect"""
    # Load and process the main video
    background = VideoFileClip(video_path)
    overlay = VideoFileClip(video_path)
    
    # Resize overlay to 70%
    overlay = overlay.resize(0.7)
    
    # Get dimensions
    w, h = background.size
    
    # Create blurred background
    background_frames = [np.ma.masked_array(frame) for frame in background.iter_frames()]
    blurred_frames = [cv2.blur(frame, (15, 15)) for frame in background_frames]
    blurred_background = ImageSequenceClip(blurred_frames, fps=background.fps)
    
    # Position overlay
    position = (w/2 - overlay.w/2, h/2 - overlay.h/2)
    composite = CompositeVideoClip([blurred_background, overlay.set_position(position)])
    
    # Crop to 9:16 aspect ratio
    crop_width = int(h * 9/16)
    crop_height = int(w * 9/16)
    x1 = int((w - crop_width) / 2)
    y1 = int((h - crop_height) / 2)
    
    cropped = composite.crop(x1, y1, x1 + crop_width, y1 + crop_height)
    resized = cropped.resize((1080, 1920))
    
    # Add outro
    outro = VideoFileClip(outro_path)
    final_video = concatenate_videoclips([resized, outro], method="compose")
    
    output_path = os.path.join(output_dir, f"YouTube_{filename}")
    final_video.write_videofile(output_path, codec='libx264', bitrate='50M')
    
    # Clean up
    background.close()
    overlay.close()
    outro.close()
    final_video.close()

def main():
    parser = argparse.ArgumentParser(description='Process gaming videos for YouTube Shorts and Twitter')
    parser.add_argument('--input-dir', required=True, help='Directory containing input videos')
    parser.add_argument('--output-dir', required=True, help='Base directory for output videos')
    parser.add_argument('--archive-dir', required=True, help='Directory for archiving processed videos')
    parser.add_argument('--twitter-outro', required=True, help='Path to Twitter outro video')
    parser.add_argument('--youtube-outro', required=True, help='Path to YouTube outro video')
    
    args = parser.parse_args()
    
    process_videos(
        args.input_dir,
        args.output_dir,
        args.archive_dir,
        args.twitter_outro,
        args.youtube_outro
    )

if __name__ == "__main__":
    main()
