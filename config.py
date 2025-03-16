import json 
from google.genai import types
from google import genai
from typing import Optional,List,Dict,Any
from pydantic import BaseModel
from dotenv import load_dotenv
from datetime import datetime, timedelta
import os 
import yt_dlp
import logging
from pprint import pprint
load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")

if api_key is None: 
    print('API Key Not Found ')
client = genai.Client(api_key=api_key)

logging.basicConfig(
    filename="youtube_summary.log",
    filemode='w',
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

class People(BaseModel):
    name: str
    background: Optional[str] = None

class Summary(BaseModel):
    topic: str
    people: List[People]
    released_year: int
    video_summary: str

class YouTubeSummary:
    """
    A class to analyse YouTube videos using Gemini AI.

    This class extracts metadata from YouTube videos, formats a structured prompt,
    and generates a summary using Gemini AI.
    """

    def __init__(
            self, 
            client: genai.Client, 
            youtube_url: str, 
            model: str = "gemini-1.5-pro"
            ) -> None:
        """
        Initialises the YouTubeSummary instance.

        Args:
            client (genai.Client): The Gemini API client.
            youtube_url (str): The URL of the YouTube video.
            model (str, optional): The AI model to use. Defaults to "gemini-1.5-pro".
        """
        logging.info("✅ Created YouTubeSummary instance")
        self.client = client
        self.youtube_url = youtube_url
        self.model = model
        self.contextual_metadata: Optional[Dict[str]] = None  # Stores video metadata

    def set_youtube_url(self, youtube_url: str) -> None:
        """
        Updates the YouTube video URL without reinitializing the class.

        Args:
            youtube_url (str): The new YouTube video URL.
        """
        logging.info(f"🔄 Updating YouTube URL to {youtube_url}")
        self.youtube_url = youtube_url
        self.contextual_metadata = None  # Reset metadata so it fetches again

    def _fetch_metadata(self) -> None:
        """
        Fetches and stores metadata for the given YouTube video.

        This method should be called before generating a video summary.
        """
        logging.info("📥 Fetching YouTube video metadata...")

        try:
            ydl_opts = {"quiet": True}  # Suppress verbose output
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(self.youtube_url, download=False)
                video_details = ydl.sanitize_info(info)

            self.contextual_metadata = {
                "title": video_details.get("title"),
                "uploader": video_details.get("uploader"),
                "channel_url": video_details.get("channel_url"),
                "upload_date": video_details.get("upload_date"),
                "description": video_details.get("description", "No description available."),
                "tags": video_details.get("tags", []),
                "categories": video_details.get("categories", []),
                "view_count": video_details.get("view_count"),
                "like_count": video_details.get("like_count"),
                "duration": video_details.get("duration"),
                "webpage_url": video_details.get("webpage_url"),
                "thumbnail": video_details.get("thumbnail"),
                "chapters": video_details.get("chapters", []),
                "subtitles": {
                    lang: sub[0]["url"]
                    for lang, sub in video_details.get("subtitles", {}).items()
                },  # URLs to subtitles, if available
            }

            logging.info("✅ Metadata successfully fetched")
        except Exception as e:
            logging.error(f"❌ Failed to fetch metadata: {e}")
            self.contextual_metadata = None

    def generate_summary(self) -> Optional[Dict[str, Any]]:
        """
        Generates a video summary using Gemini AI, incorporating metadata.

        Args:
            prompt (str): The prompt used for generating the summary.

        Returns:
            Optional[Dict[str, Any]]: The AI-generated summary if successful, otherwise None.
        """
        logging.info("📝 Generating video summary...")

        # Ensure metadata is available before proceeding - Should be None by default 
        prompt =  """
            Analyse this video & generate a video_summary

            Extract who is speaking in this video. Then summarise their background.


            AI & Technology topic- Focus On:
            What are they key elements they are talking about
            What are the general trends 
            Are there any key advancedments that are notable 

            For each key topic:

            Summarise the main points and some additional detail provide a timestamp if possible.
            """
        if self.contextual_metadata is None:
            logging.warning("⚠️ Metadata not found! Fetching now...")
            self._fetch_metadata()

        if self.contextual_metadata is None:
            logging.error("❌ Failed to fetch video metadata. Aborting summary generation.")
            return None
        # Format metadata for bettercontext
        metadata_text = f"""
        # Video Metadata
        * Title: {self.contextual_metadata["title"]}
        * Uploader: {self.contextual_metadata["uploader"]}
        * Upload Date: {self.contextual_metadata["upload_date"]}
        * Description: {self.contextual_metadata["description"][:500]}...
        * Tags: {", ".join(self.contextual_metadata["tags"])}
        * Categories: {", ".join(self.contextual_metadata["categories"])}
        * View Count: {self.contextual_metadata["view_count"]}
        * Like Count: {self.contextual_metadata["like_count"]}
        * Subtitles Available: {"Yes" if self.contextual_metadata["subtitles"] else "No"}
        """
        logging.info(metadata_text)
        print(metadata_text)

        # Append metadata to prompt
        final_prompt = f"{prompt}\n\n{metadata_text}"
        logging.info("🚀 Sending request to Gemini AI...")

        try:
            response = self.client.models.generate_content(
                model=self.model,
                contents=types.Content(
                    parts=[
                        types.Part(text=final_prompt),
                        types.Part(file_data=types.FileData(file_uri=self.youtube_url))
                        ]
                ),
                config=types.GenerateContentConfig(
                    response_mime_type="application/json",
                    response_schema=Summary
                )
            )

            logging.info("✅ Summary successfully generated")
            logging.info(response.parsed)
            return response.parsed  # Return structured response
        except Exception as e:
            logging.error(f"❌ Error during summary generation: {e}")
            return None



#  Used video below for testing 
# youtube_url = "https://www.youtube.com/watch?v=vdbMuq1SS8c"
# youtube_url = "https://www.youtube.com/watch?v=8w4tohBnJN4"
# youtube_url = 'https://www.youtube.com/watch?v=_Krpcp6nl08' # Transformers
# summary = YouTubeSummary(client, youtube_url=youtube_url)



# response = summary.generate_summary()

# pprint(response)